"""WhatsApp Cloud API webhook (Phase G).

GET verifies the webhook with the configured verify token (Meta handshake). POST
receives inbound messages: an unknown sender is rejected, and a known user can confirm
a pending order intent with "CONFIRM <intentId>". Outbound replies go through the
configured WhatsApp channel (the dev echo channel when Meta is not configured).
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from app.core.config import Settings
from app.core.dependencies import get_container, get_settings
from app.infra.factory import Container
from app.infra.repo.auth_repo import AuthRepository
from app.services.trade_service import TradeService

logger = logging.getLogger("quantastica.whatsapp")
router = APIRouter(prefix="/whatsapp")


@router.get("/webhook")
async def verify(request: Request, settings: Settings = Depends(get_settings)):
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and settings.whatsapp_verify_token
        and params.get("hub.verify_token") == settings.whatsapp_verify_token
    ):
        return PlainTextResponse(params.get("hub.challenge", ""))
    return JSONResponse(status_code=403, content={"ok": False})


def _extract_message(payload: dict) -> tuple[str, str] | None:
    try:
        value = payload["entry"][0]["changes"][0]["value"]
        message = value["messages"][0]
        return message["from"], message["text"]["body"].strip()
    except (KeyError, IndexError, TypeError):
        return None


@router.post("/webhook")
async def inbound(
    request: Request,
    settings: Settings = Depends(get_settings),
    container: Container = Depends(get_container),
):
    payload = await request.json()
    parsed = _extract_message(payload)
    if parsed is None:
        return JSONResponse(content={"ok": True})

    from_number, text = parsed
    e164 = from_number if from_number.startswith("+") else f"+{from_number}"
    auth = AuthRepository(container.session_factory)
    user = await auth.get_user_by_phone(e164)

    channel = container.provider("whatsapp")  # type: ignore[assignment]
    if user is None:
        await auth.audit(None, "whatsapp.unknown_sender", {"from": e164})
        await channel.send(e164, "This number is not linked to a Quantastica account.")
        return JSONResponse(content={"ok": True})

    reply = await _handle_command(container, auth, user, text)
    await channel.send(e164, reply)
    return JSONResponse(content={"ok": True})


async def _handle_command(container: Container, auth: AuthRepository, user, text: str) -> str:
    user_id = user.id
    settings = container.settings
    parts = text.split()
    command = parts[0].upper() if parts else ""
    is_trading = command in ("CONFIRM", "YES", "CANCEL", "NO", "BUY", "SELL")
    # A WhatsApp number must be OTP-verified before it can move money.
    if is_trading and not user.phone_verified:
        await auth.audit(user_id, "whatsapp.unverified_command", {"command": command})
        return "Verify this number in the app before sending trade commands."
    if command in ("CONFIRM", "YES") and len(parts) >= 2:
        intent_id = parts[1]
        try:
            intent = await TradeService(container).approve_and_execute(user_id, intent_id)
        except Exception as exc:  # surface a safe message to the user
            await auth.audit(user_id, "whatsapp.confirm_failed", {"intentId": intent_id})
            return f"Could not execute {intent_id}: {exc}"
        return (
            f"Order {intent.id} {intent.status.value}. "
            f"{intent.side.value} {intent.quantity} {intent.symbol} "
            f"at {intent.fill_price}."
        )
    if command in ("CANCEL", "NO") and len(parts) >= 2:
        await TradeService(container).cancel_intent(user_id, parts[1])
        return f"Cancelled {parts[1]}."
    lower = text.lower()
    if "queue" in lower or "exception" in lower:
        from app.infra.repo.book_repo import BookRepository
        from app.services.desk_service import DeskService
        from app.speech.provider import queue_script

        queue = await DeskService(BookRepository(container.session_factory)).queue("hh_mehta")
        return queue_script(queue["exceptions"])
    if command in ("BUY", "SELL") or "buy " in lower or "sell " in lower:
        if not settings.trading_chat_enabled:
            return "Conversational trading is off. Paper intents stay behind TRADING_CHAT_ENABLED."
        from app.schemas.common import OrderSide, OrderType
        from app.schemas.trade import CreateOrderIntent
        from app.trading.intents import estimate_charges, parse_order_text, pretrade_notes

        draft = parse_order_text(text)
        if draft.needs_clarification:
            return draft.clarification or "Clarify the order."
        portfolios = await container.repository.list_portfolios(user_id)
        if not portfolios:
            return "No portfolio on this account. Seed the desk first."
        intent = await TradeService(container).create_intent(
            user_id,
            CreateOrderIntent(
                portfolio_id=portfolios[0].id,
                symbol=draft.symbol,
                side=OrderSide(draft.side),
                quantity=draft.quantity,
                order_type=OrderType.market,
            ),
            source="whatsapp",
        )
        notes = pretrade_notes(draft.symbol, draft.side, None)
        charges = estimate_charges(intent.notional_inr, draft.side)
        return (
            f"PAPER {draft.side} {draft.quantity} {draft.symbol}. "
            f"Est. value Rs {intent.notional_inr:,.0f}. Charges Rs {charges['totalInr']:,.0f}. "
            f"{' '.join(notes)} "
            f"Reply CONFIRM {intent.id} within 10 minutes. No order without confirmation."
        )
    return (
        "Commands: 'CONFIRM <intentId>' to execute a pending order, "
        "'CANCEL <intentId>' to cancel it, or 'queue' for the Mehta digest."
    )
