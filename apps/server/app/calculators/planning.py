"""SIP/goal math, EMI, affordability (FOIR), and Monte Carlo simulation.
Pure code, standard future-value formulas, INR throughout."""

from __future__ import annotations

import random
from math import sqrt

from pydantic import Field

from app.schemas.base import Contract


def required_monthly_sip(target: float, years: float, annual_return: float) -> float:
    """Monthly SIP for a future value target: P = FV * r / ((1+r)^n - 1)."""
    n = int(round(years * 12))
    if n <= 0:
        raise ValueError("years must be positive")
    r = annual_return / 12.0
    if r == 0:
        return target / n
    return target * r / ((1 + r) ** n - 1)


def step_up_sip_first_month(
    target: float, years: float, annual_return: float, annual_step_up: float
) -> float:
    """First-month SIP when the contribution steps up annually. Solved by scaling:
    the FV is linear in the starting SIP."""
    fv_of_one = _step_up_fv(1.0, years, annual_return, annual_step_up)
    return target / fv_of_one


def _step_up_fv(first_sip: float, years: float, annual_return: float, step_up: float) -> float:
    r = annual_return / 12.0
    n = int(round(years * 12))
    fv, sip = 0.0, first_sip
    for month in range(n):
        if month > 0 and month % 12 == 0:
            sip *= 1 + step_up
        fv = (fv + sip) * (1 + r)
    return fv


def emi(principal: float, annual_rate: float, years: float) -> float:
    n = int(round(years * 12))
    r = annual_rate / 12.0
    if r == 0:
        return principal / n
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


class AffordabilityInput(Contract):
    purchase_cost: float = Field(gt=0)
    down_payment: float = Field(ge=0)
    loan_rate: float = Field(gt=0, lt=1)
    loan_years: float = Field(gt=0)
    monthly_income: float = Field(gt=0)
    existing_emi: float = Field(default=0, ge=0)
    liquid_savings: float = Field(ge=0)
    monthly_expenses: float = Field(default=0, ge=0)


class AffordabilityResult(Contract):
    new_emi: float
    total_emi: float
    foir: float
    foir_band_ok: bool
    cash_buffer_after_purchase: float
    emergency_fund_months: float
    affordable: bool


FOIR_LIMIT = 0.50


def affordability(data: AffordabilityInput) -> AffordabilityResult:
    loan_amount = max(0.0, data.purchase_cost - data.down_payment)
    new_emi = emi(loan_amount, data.loan_rate, data.loan_years) if loan_amount else 0.0
    total_emi = new_emi + data.existing_emi
    foir = total_emi / data.monthly_income
    buffer = data.liquid_savings - data.down_payment
    outflow = data.monthly_expenses + total_emi
    months = buffer / outflow if outflow > 0 else float("inf")
    foir_ok = foir <= FOIR_LIMIT
    return AffordabilityResult(
        new_emi=round(new_emi, 2),
        total_emi=round(total_emi, 2),
        foir=round(foir, 4),
        foir_band_ok=foir_ok,
        cash_buffer_after_purchase=round(buffer, 2),
        emergency_fund_months=round(months, 1),
        affordable=foir_ok and buffer >= 0 and months >= 3,
    )


class SimulationResult(Contract):
    horizon_years: float
    monthly_sip: float
    p10: float
    p50: float
    p90: float


def monte_carlo_sip(
    monthly_sip: float,
    years: float,
    annual_return: float,
    annual_volatility: float,
    paths: int = 2000,
    rng_seed: int | None = None,
) -> SimulationResult:
    rng = random.Random(rng_seed)
    n = int(round(years * 12))
    mu = annual_return / 12.0
    sigma = annual_volatility / sqrt(12.0)
    finals: list[float] = []
    for _ in range(paths):
        value = 0.0
        for _ in range(n):
            value = (value + monthly_sip) * (1 + rng.gauss(mu, sigma))
        finals.append(value)
    finals.sort()
    return SimulationResult(
        horizon_years=years,
        monthly_sip=monthly_sip,
        p10=round(finals[int(0.10 * paths)], 2),
        p50=round(finals[int(0.50 * paths)], 2),
        p90=round(finals[int(0.90 * paths)], 2),
    )
