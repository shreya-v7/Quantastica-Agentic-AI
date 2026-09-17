"""Structured order intents. LLM optional; regex first. No auto-execution."""

from __future__ import annotations

import re

from app.core.errors import ValidationError
from app.india.market_hours import is_market_open
from app.schemas.base import Contract

_ORDER = re.compile(
    r"\b(buy|sell)\s+(\d+(?:\.\d+)?)\s+([a-z0-9.]+)\b",
    re.I,
)
_HALF = re.compile(r"\bsell\s+half\s+(?:my\s+)?([a-z0-9.]+)\b", re.I)


class OrderIntentDraft(Contract):
    symbol: str
    side: str
    quantity: float
    order_type: str = "market"
    needs_clarification: bool = False
    clarification: str | None = None


def parse_order_text(text: str, half_qty: float | None = None) -> OrderIntentDraft:
    lower = text.lower()
    if "ignore rules" in lower or "tell me to buy" in lower:
        raise ValidationError("Prompt injection refused.")
    half = _HALF.search(text)
    if half:
        if half_qty is None:
            return OrderIntentDraft(
                symbol=half.group(1).upper(),
                side="sell",
                quantity=0,
                needs_clarification=True,
                clarification="What quantity is half of that holding?",
            )
        return OrderIntentDraft(symbol=half.group(1).upper(), side="sell", quantity=half_qty)
    match = _ORDER.search(text)
    if match is None:
        return OrderIntentDraft(
            symbol="",
            side="buy",
            quantity=0,
            needs_clarification=True,
            clarification="Say buy or sell, a quantity, and a symbol. Example: buy 10 RELIANCE.NS",
        )
    side, qty, symbol = match.group(1).lower(), float(match.group(2)), match.group(3).upper()
    if "." not in symbol:
        symbol = f"{symbol}.NS"
    return OrderIntentDraft(symbol=symbol, side=side, quantity=qty)


def pretrade_notes(symbol: str, side: str, lot_clock_extra: float | None) -> list[str]:
    notes: list[str] = []
    if not is_market_open():
        notes.append("NSE regular session is closed. Paper orders still record.")
    if side == "sell" and lot_clock_extra and lot_clock_extra > 0:
        notes.append(
            f"This sale is STCG relative to waiting. "
            f"Extra tax if sold today: Rs {lot_clock_extra:,.0f}."
        )
    notes.append("Informational only. Not a recommendation to buy or sell.")
    return notes


def estimate_charges(notional_inr: float, side: str) -> dict[str, float]:
    """Rough delivery equity charges for a paper summary. Not a broker invoice."""
    stt = round(notional_inr * (0.001 if side == "sell" else 0.0001), 2)
    stamp = round(notional_inr * 0.00015, 2) if side == "buy" else 0.0
    total = round(stt + stamp, 2)
    return {"sttInr": stt, "stampInr": stamp, "brokerageInr": 0.0, "totalInr": total}
