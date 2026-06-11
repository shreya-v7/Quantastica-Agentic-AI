"""Indian income tax engine. Pure code, no LLM. Compares OLD vs NEW regime with a
line-itemed breakdown. Rule tables are versioned per assessment year in tax_rules/."""

from __future__ import annotations

from pydantic import Field

from app.calculators.tax_rules import ay_2025_26
from app.core.errors import ValidationError
from app.schemas.base import Contract

RULES_BY_AY = {"2025-26": ay_2025_26}


class TaxInput(Contract):
    assessment_year: str = "2025-26"
    basic_salary: float = Field(ge=0)
    hra_received: float = Field(default=0, ge=0)
    other_income: float = Field(default=0, ge=0)
    rent_paid: float = Field(default=0, ge=0)
    metro_city: bool = True
    deduction_80c: float = Field(default=0, ge=0)
    health_premium_self: float = Field(default=0, ge=0)
    age_60_plus: bool = False
    nps_80ccd_1b: float = Field(default=0, ge=0)
    home_loan_interest: float = Field(default=0, ge=0)


class TaxLine(Contract):
    label: str
    amount: float


class RegimeResult(Contract):
    regime: str
    gross_income: float
    taxable_income: float
    lines: list[TaxLine]
    slab_tax: float
    rebate_87a: float
    surcharge: float
    cess: float
    total_tax: float


class TaxComparison(Contract):
    assessment_year: str
    old_regime: RegimeResult
    new_regime: RegimeResult
    recommended: str
    saving_inr: float


def slab_tax(taxable: float, slabs: list[tuple[float | None, float]]) -> float:
    tax, lower = 0.0, 0.0
    for upper, rate in slabs:
        cap = taxable if upper is None else min(taxable, upper)
        if cap > lower:
            tax += (cap - lower) * rate
        if upper is None or taxable <= upper:
            break
        lower = upper
    return tax


def surcharge_with_marginal_relief(
    taxable: float, base_tax: float, bands: list[tuple[float, float]],
    slabs: list[tuple[float | None, float]],
) -> float:
    for threshold, rate in bands:  # bands ordered highest first
        if taxable > threshold:
            surcharge = base_tax * rate
            # Marginal relief: tax plus surcharge cannot exceed the tax at the
            # threshold plus the income above the threshold.
            tax_at_threshold = slab_tax(threshold, slabs)
            lower_rate = next((r for t, r in bands if threshold > t), 0.0)
            cap = tax_at_threshold * (1 + lower_rate) + (taxable - threshold)
            return min(base_tax + surcharge, cap) - base_tax
    return 0.0


def hra_exemption(basic: float, hra_received: float, rent_paid: float, metro: bool) -> float:
    if rent_paid <= 0 or hra_received <= 0:
        return 0.0
    return max(
        0.0,
        min(hra_received, rent_paid - 0.10 * basic, (0.50 if metro else 0.40) * basic),
    )


def _regime(name: str, rules: dict, gross: float, deductions: list[TaxLine]) -> RegimeResult:
    total_deductions = sum(line.amount for line in deductions)
    taxable = max(0.0, gross - total_deductions)
    base = slab_tax(taxable, rules["slabs"])
    eligible = taxable <= rules["rebate_87a_income_cap"]
    rebate = min(base, rules["rebate_87a_max"]) if eligible else 0.0
    after_rebate = base - rebate
    surcharge = surcharge_with_marginal_relief(
        taxable, after_rebate, rules["surcharge"], rules["slabs"]
    )
    cess = (after_rebate + surcharge) * rules["cess"]
    return RegimeResult(
        regime=name,
        gross_income=round(gross, 2),
        taxable_income=round(taxable, 2),
        lines=deductions,
        slab_tax=round(base, 2),
        rebate_87a=round(rebate, 2),
        surcharge=round(surcharge, 2),
        cess=round(cess, 2),
        total_tax=round(after_rebate + surcharge + cess, 2),
    )


def compare_regimes(data: TaxInput) -> TaxComparison:
    if data.assessment_year not in RULES_BY_AY:
        raise ValidationError(
            f"No tax rules for AY {data.assessment_year}. "
            f"Available: {', '.join(RULES_BY_AY)}"
        )
    rules = RULES_BY_AY[data.assessment_year]
    caps = rules.DEDUCTION_CAPS
    gross = data.basic_salary + data.hra_received + data.other_income

    old_lines = [
        TaxLine(label="Standard deduction", amount=rules.OLD_REGIME["standard_deduction"]),
        TaxLine(label="80C (capped)", amount=min(data.deduction_80c, caps["80c"])),
        TaxLine(
            label="80D health premium",
            amount=min(
                data.health_premium_self,
                caps["80d_self_60_plus"] if data.age_60_plus else caps["80d_self_below_60"],
            ),
        ),
        TaxLine(label="80CCD(1B) NPS", amount=min(data.nps_80ccd_1b, caps["80ccd_1b"])),
        TaxLine(
            label="24(b) home loan interest",
            amount=min(data.home_loan_interest, caps["24b_self_occupied"]),
        ),
        TaxLine(
            label="HRA exemption",
            amount=round(
                hra_exemption(
                    data.basic_salary, data.hra_received, data.rent_paid, data.metro_city
                ),
                2,
            ),
        ),
    ]
    new_lines = [
        TaxLine(label="Standard deduction", amount=rules.NEW_REGIME["standard_deduction"])
    ]

    old = _regime("old", rules.OLD_REGIME, gross, [ln for ln in old_lines if ln.amount > 0])
    new = _regime("new", rules.NEW_REGIME, gross, new_lines)
    recommended = "old" if old.total_tax < new.total_tax else "new"
    return TaxComparison(
        assessment_year=data.assessment_year,
        old_regime=old,
        new_regime=new,
        recommended=recommended,
        saving_inr=round(abs(old.total_tax - new.total_tax), 2),
    )
