"""Trade execution service.

Every order is an OrderIntent first. Creation runs pre-trade guardrails (kill switch,
per-order notional cap, open-intent cap). Execution is a separate, approval-gated step
that re-checks the kill switch and the daily notional cap, enforces market hours for
live orders, selects the broker (paper by default, Kite only when live is fully
configured in prod), and applies the fill atomically. Every transition is audited.
"""

from __future__ import annotations

from app.core.errors import (
    ForbiddenError,
    MarketClosedError,
    NotFoundError,
    TradeLimitError,
)
from app.india.market_hours import is_market_open
from app.infra.factory import Container
from app.infra.repo.auth_repo import AuthRepository
from app.infra.repo.trade_repo import TradeRepository
from app.providers.broker.base import Broker, BrokerOrder
from app.providers.marketdata.base import validate_symbol
from app.schemas.common import OrderStatus, OrderType, TradingMode
from app.schemas.trade import CreateOrderIntent, OrderIntent


class TradeService:
    def __init__(self, container: Container):
        self._c = container
        self._settings = container.settings
        self._trades = TradeRepository(container.session_factory)
        self._auth = AuthRepository(container.session_factory)

    async def _assert_can_trade(self, user_id: str) -> None:
        user = await self._auth.get_user(user_id)
        if user is None:
            raise NotFoundError("Unknown user")
        if user.trading_disabled:
            raise ForbiddenError("Trading is disabled for this account (kill switch active).")

    def _mode(self) -> TradingMode:
        return TradingMode.live if self._settings.live_trading_configured else TradingMode.paper

    async def _reference_price(self, symbol: str, req: CreateOrderIntent) -> float:
        if req.order_type == OrderType.limit and req.limit_price:
            return req.limit_price
        quote = await self._c.provider("marketdata").quote(symbol)  # type: ignore[attr-defined]
        return quote.price

    async def create_intent(
        self, user_id: str, req: CreateOrderIntent, source: str = "manual"
    ) -> OrderIntent:
        await self._assert_can_trade(user_id)
        symbol = validate_symbol(req.symbol)
        req = req.model_copy(update={"symbol": symbol})

        price = await self._reference_price(symbol, req)
        notional = price * req.quantity
        if notional > self._settings.trade_max_order_notional_inr:
            raise TradeLimitError(
                f"Order notional {notional:.0f} exceeds the per-order cap "
                f"{self._settings.trade_max_order_notional_inr:.0f}."
            )
        open_count = await self._trades.count_open(user_id)
        if open_count >= self._settings.trade_max_open_intents:
            raise TradeLimitError(
                f"You already have {open_count} open intents (cap "
                f"{self._settings.trade_max_open_intents}). Resolve some first."
            )
        intent = await self._trades.create(
            user_id, req, self._mode().value, notional, source
        )
        await self._auth.audit(
            user_id,
            "trade.intent_created",
            {"intentId": intent.id, "symbol": symbol, "notional": notional, "source": source},
        )
        return intent

    async def approve_and_execute(self, user_id: str, intent_id: str) -> OrderIntent:
        await self._assert_can_trade(user_id)
        row = await self._trades.get(user_id, intent_id)
        if row is None:
            raise NotFoundError(f"Order intent '{intent_id}' not found")
        if row.status != OrderStatus.pending_approval.value:
            raise TradeLimitError(
                f"Intent is '{row.status}', only pending_approval intents can be executed."
            )

        notional = float(row.notional_inr)
        used = await self._trades.filled_notional_today(user_id)
        if used + notional > self._settings.trade_max_daily_notional_inr:
            raise TradeLimitError(
                f"Daily notional cap {self._settings.trade_max_daily_notional_inr:.0f} "
                f"would be exceeded (used {used:.0f} + {notional:.0f})."
            )

        mode = TradingMode(row.mode)
        if mode == TradingMode.live:
            user = await self._auth.get_user(user_id)
            if self._settings.auth_enabled and not (user and user.totp_enabled):
                raise ForbiddenError("Enable 2FA (TOTP) before placing live orders.")
            if not is_market_open():
                raise MarketClosedError(
                    "NSE is closed. Live orders run only during market hours."
                )

        await self._trades.set_status(user_id, intent_id, OrderStatus.submitted)
        broker: Broker = self._c.provider(
            "broker_live" if mode == TradingMode.live else "broker_paper"
        )  # type: ignore[assignment]
        order = BrokerOrder(
            symbol=row.symbol,
            side=row.side,  # type: ignore[arg-type]
            quantity=float(row.quantity),
            order_type=row.order_type,  # type: ignore[arg-type]
            limit_price=float(row.limit_price) if row.limit_price is not None else None,
        )
        result = await broker.place_order(order)
        if result.status == "rejected":
            await self._trades.set_status(
                user_id, intent_id, OrderStatus.rejected, reason=result.reason,
                broker_order_id=result.broker_order_id,
            )
            await self._auth.audit(
                user_id, "trade.rejected",
                {"intentId": intent_id, "reason": result.reason},
            )
            return await self.get_intent(user_id, intent_id)

        intent = await self._trades.apply_fill(
            user_id, intent_id, result.fill_price or 0.0, result.broker_order_id
        )
        await self._auth.audit(
            user_id, "trade.filled",
            {"intentId": intent_id, "fillPrice": result.fill_price, "mode": mode.value},
        )
        return intent

    async def cancel_intent(self, user_id: str, intent_id: str) -> OrderIntent:
        row = await self._trades.get(user_id, intent_id)
        if row is None:
            raise NotFoundError(f"Order intent '{intent_id}' not found")
        if row.status != OrderStatus.pending_approval.value:
            raise TradeLimitError("Only pending_approval intents can be cancelled.")
        await self._trades.set_status(user_id, intent_id, OrderStatus.cancelled)
        await self._auth.audit(user_id, "trade.cancelled", {"intentId": intent_id})
        return await self.get_intent(user_id, intent_id)

    async def get_intent(self, user_id: str, intent_id: str) -> OrderIntent:
        row = await self._trades.get(user_id, intent_id)
        if row is None:
            raise NotFoundError(f"Order intent '{intent_id}' not found")
        return TradeRepository._intent(row)

    async def list_intents(self, user_id: str) -> list[OrderIntent]:
        return await self._trades.list(user_id)

    async def set_kill_switch(self, user_id: str, disabled: bool) -> None:
        await self._auth.set_trading_disabled(user_id, disabled)
        await self._auth.audit(user_id, "trade.kill_switch", {"disabled": disabled})
