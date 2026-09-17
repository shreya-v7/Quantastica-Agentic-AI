"""Maker-checker over extracted money fields. Sibling of extractors, not a child."""
from __future__ import annotations

from .guard import parse_amounts


def verify_money_fields(payload: dict, max_retries_used: int = 0) -> dict:
    """Catch injected numeric errors against source quotes. Fail closed after 2 tries."""
    issues: list[str] = []
    for key, value in payload.items():
        if not isinstance(value, dict):
            continue
        if "amount" not in value or "source_quote" not in value:
            continue
        quoted = parse_amounts(str(value.get("source_quote") or ""))
        amount = round(float(value["amount"]), 2)
        if quoted and amount not in quoted:
            issues.append(key)
        confidence = float(value.get("confidence") or payload.get("confidence") or 1)
        if confidence < 0.7:
            issues.append(key)
    needs_review = bool(issues) and max_retries_used >= 2
    retry = bool(issues) and max_retries_used < 2
    return {
        "ok": not issues,
        "issues": issues,
        "retry": retry,
        "needs_review": needs_review,
    }
