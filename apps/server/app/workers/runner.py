"""Background worker: evaluates price alerts and automation rules on a fixed interval.

Only the Redis leader evaluates. Each rule is wrapped so one failure never stops the
loop. Quotes are fetched once per symbol per tick. Alert and automation firing are
cooldown- and cap-gated by the same logic the API uses.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from datetime import UTC, datetime

from app.agents.sentiment import run_sentiment
from app.core.config import Settings, get_settings
from app.core.leader import LeaderLock
from app.infra.factory import Container, build_container
from app.infra.repo.alert_repo import AlertRepository
from app.infra.repo.auth_repo import AuthRepository
from app.infra.repo.automation_repo import AutomationRepository
from app.providers.marketdata.base import Quote
from app.schemas.common import AlertOperator
from app.schemas.trade import CreateOrderIntent
from app.services.automation_service import fire_decision
from app.services.trade_service import TradeService

logger = logging.getLogger("quantastica.worker")

LEADER_KEY = "quantastica:worker:leader"


async def _quote_map(container: Container, symbols: set[str]) -> dict[str, Quote]:
    quotes: dict[str, Quote] = {}
    provider = container.providers.get("marketdata")
    if provider is None or not provider.ready:
        return quotes
    for symbol in symbols:
        try:
            quotes[symbol] = await provider.instance.quote(symbol)  # type: ignore[union-attr]
        except Exception as exc:
            logger.warning("quote failed for %s: %s", symbol, exc)
    return quotes


def alert_met(kind: str, operator: str, quote: Quote, threshold: float) -> bool:
    """Pure trigger predicate for price and percent-move alerts."""
    if kind == "percent_move":
        if not quote.previous_close:
            return False
        move = abs(quote.price - quote.previous_close) / quote.previous_close
        return move >= threshold
    if operator == AlertOperator.above.value:
        return quote.price >= threshold
    return quote.price <= threshold


def _in_cooldown(alert, now: datetime) -> bool:
    return bool(
        alert.last_triggered_at
        and (now - alert.last_triggered_at).total_seconds() < alert.cooldown_seconds
    )


async def evaluate_alerts(container: Container) -> int:
    repo = AlertRepository(container.session_factory)
    auth = AuthRepository(container.session_factory)
    alerts = await repo.list_active_globally()
    price_alerts = [a for a in alerts if a.kind in ("price", "percent_move")]
    flip_alerts = [a for a in alerts if a.kind == "sentiment_flip"]
    quotes = await _quote_map(container, {a.symbol for a in price_alerts})
    fired = 0
    now = datetime.now(UTC)

    for alert in price_alerts:
        quote = quotes.get(alert.symbol)
        if quote is None or not alert_met(alert.kind, alert.operator, quote, alert.threshold):
            continue
        if _in_cooldown(alert, now):
            continue
        body = (
            f"{alert.symbol} moved {alert.threshold:.0%} today (now {quote.price})."
            if alert.kind == "percent_move"
            else f"{alert.symbol} is {quote.price} ({alert.operator} {alert.threshold})."
        )
        fired += await _deliver(container, auth, repo, alert, f"Alert '{alert.name}': {body}")

    for alert in flip_alerts:
        fired += await _evaluate_sentiment_flip(container, auth, repo, alert, now)
    return fired


async def _deliver(container, auth, repo, alert, message: str, label: str | None = None) -> int:
    user = await auth.get_user(alert.user_id)
    try:
        if user and user.phone:
            await container.provider("whatsapp").send(user.phone, message)  # type: ignore
        await repo.record_trigger(alert.id, label)
        await auth.audit(alert.user_id, "alert.fired", {"alertId": alert.id, "kind": alert.kind})
        return 1
    except Exception as exc:
        logger.warning("alert %s delivery failed: %s", alert.id, exc)
        return 0


async def _evaluate_sentiment_flip(container, auth, repo, alert, now: datetime) -> int:
    if _in_cooldown(alert, now):
        return 0
    news = container.providers.get("news")
    if news is None or not news.ready:
        return 0
    try:
        items = await news.instance.search(alert.symbol.split(".")[0], limit=10)
        result = await run_sentiment(
            container.llm, alert.symbol, items, container.settings.llm_retries
        )
    except Exception as exc:
        logger.warning("sentiment flip eval failed for %s: %s", alert.symbol, exc)
        return 0
    label = result.label
    if alert.last_label and alert.last_label != label:
        message = (
            f"Alert '{alert.name}': {alert.symbol} sentiment flipped "
            f"{alert.last_label} -> {label}."
        )
        return await _deliver(container, auth, repo, alert, message, label=label)
    await repo.record_label(alert.id, label)
    return 0


async def evaluate_automation(container: Container, settings: Settings) -> int:
    repo = AutomationRepository(container.session_factory)
    auth = AuthRepository(container.session_factory)
    rules = await repo.list_active_globally()
    prices = await _quote_map(container, {r.trigger["symbol"] for r in rules})
    fired = 0
    now = datetime.now(UTC)
    for rule in rules:
        price = prices.get(rule.trigger["symbol"])
        if price is None:
            continue
        user = await auth.get_user(rule.user_id)
        enabled = bool(user and user.automation_enabled and not user.trading_disabled)
        should, reason = fire_decision(rule, price, now, enabled, settings)
        if not should:
            continue
        try:
            action = rule.action
            req = CreateOrderIntent.model_validate(
                {
                    "portfolioId": rule.portfolio_id,
                    "symbol": rule.trigger["symbol"],
                    "side": action["side"],
                    "quantity": action["quantity"],
                    "orderType": action.get("orderType", "market"),
                    "limitPrice": action.get("limitPrice"),
                }
            )
            service = TradeService(container)
            intent = await service.create_intent(rule.user_id, req, source="automation")
            executed = await service.approve_and_execute(rule.user_id, intent.id)
            await repo.record_fire(rule.id, executed.notional_inr)
            await auth.audit(
                rule.user_id, "automation.fired",
                {"ruleId": rule.id, "intentId": intent.id, "status": executed.status.value},
            )
            fired += 1
        except Exception as exc:
            logger.warning("automation rule %s failed: %s", rule.id, exc)
    return fired


async def run_forever(stop: asyncio.Event | None = None) -> None:
    settings = get_settings()
    container = build_container(settings)
    lock = LeaderLock(
        container.cache, LEADER_KEY, ttl_seconds=int(settings.worker_poll_seconds * 3)
    )
    stop = stop or asyncio.Event()
    logger.info("worker started; poll=%ss", settings.worker_poll_seconds)
    try:
        while not stop.is_set():
            if await lock.acquire_or_renew():
                try:
                    alerts = await evaluate_alerts(container)
                    autos = await evaluate_automation(container, settings)
                    if alerts or autos:
                        logger.info("tick: %s alerts, %s automations fired", alerts, autos)
                except Exception as exc:
                    logger.exception("worker tick failed: %s", exc)
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(stop.wait(), timeout=settings.worker_poll_seconds)
    finally:
        await lock.release()
        await container.close()
        logger.info("worker stopped")
