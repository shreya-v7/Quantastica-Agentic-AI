from __future__ import annotations

from datetime import date

from pydantic import Field

from quantastica_kernel.contract import Contract

CALCULATOR_VERSION = "ay_2025_26"


class PolicyTable(Contract):
    name_cap: float = Field(default=0.15, gt=0, le=1)
    sector_cap: float = Field(default=0.40, gt=0, le=1)
    lot_clock_days: int = Field(default=60, ge=1)
    regime_saving_threshold: float = Field(default=10_000, ge=0)
    deduction_unused_threshold: float = Field(default=10_000, ge=0)


class ExceptionHit(Contract):
    rule_id: str
    version: str
    title: str
    rupee_delta: float
    due_date: date | None = None
    severity: str
    metric_ids: list[str]
    fingerprint: str
    calculator: str
    calculator_version: str = CALCULATOR_VERSION
    inputs: dict
    outputs: dict
