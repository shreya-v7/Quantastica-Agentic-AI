from typing import Any

from app.financial_intelligence.core.types import FinancialSnapshot, Investment, Liability


def normalize_snapshot(user_id: str, raw: dict[str, Any]) -> FinancialSnapshot:
    investments = [
        Investment(symbol=item.get("symbol", "UNKNOWN"), value=float(item.get("value", 0)))
        for item in raw.get("investments", [])
    ]
    liabilities = [
        Liability(
            type=item.get("type", "other"),
            amount=float(item.get("amount", 0)),
            rate=float(item.get("rate", 0)),
        )
        for item in raw.get("liabilities", [])
    ]

    return FinancialSnapshot(
        user_id=user_id,
        balance=float(raw.get("balance", 0)),
        investments=investments,
        liabilities=liabilities,
    )
