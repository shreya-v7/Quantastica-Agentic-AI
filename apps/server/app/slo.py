"""Google SRE multiwindow, multi-burn-rate alerting."""
from __future__ import annotations

from dataclasses import dataclass

PAGE_LONG = 1.0  # hours
PAGE_SHORT = 5 / 60
PAGE_BURN = 14.4
TICKET_LONG = 6.0
TICKET_BURN = 6.0
BUDGET = 0.001  # 99.9% availability -> 0.1% error budget / 30d


@dataclass(frozen=True)
class BurnAlert:
    severity: str
    burn: float
    reason: str


def burn_rate(error_ratio: float, slo_budget: float = BUDGET) -> float:
    """Error-budget burn multiple. 1.0 means the 30-day budget is consumed exactly."""
    if slo_budget <= 0:
        return 0.0
    return error_ratio / slo_budget


def alert(error_1h: float, error_5m: float, error_6h: float | None = None) -> BurnAlert | None:
    long_burn = error_1h / BUDGET
    short_burn = error_5m / BUDGET
    if long_burn >= PAGE_BURN and short_burn >= PAGE_BURN:
        return BurnAlert("page", long_burn, "14.4x burn over 1h confirmed by 5m")
    six = (error_6h if error_6h is not None else error_1h) / BUDGET
    if six >= TICKET_BURN:
        return BurnAlert("ticket", six, "6x burn over 6h")
    return None
