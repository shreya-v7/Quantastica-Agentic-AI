"""Deterministic loan and insurance matching. No LLM in the scoring path: products are
filtered on hard eligibility, then ranked by transparent, explainable criteria. The
optional explanation agent only narrates the already-decided ranking."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.calculators.planning import emi
from app.core.errors import ValidationError
from app.infra.repo.catalog_repo import CatalogRepository
from app.schemas.base import Contract


class LoanMatchRequest(Contract):
    loan_type: Literal["home", "personal", "car"]
    amount_inr: float = Field(gt=0)
    tenure_years: float = Field(gt=0, le=30)
    monthly_income_inr: float = Field(gt=0)
    existing_emi_inr: float = Field(default=0, ge=0)
    property_value_inr: float | None = Field(default=None, gt=0)


class LoanMatch(Contract):
    product_id: str
    provider: str
    name: str
    indicative_rate: float
    emi_inr: float
    emi_display: str
    processing_fee_inr: float
    foir_after: float
    eligible: bool
    reasons: list[str]
    score: float


class InsuranceMatchRequest(Contract):
    insurance_type: Literal["term", "health"]
    cover_inr: float = Field(gt=0)
    age: int = Field(ge=18, le=99)
    smoker: bool = False
    family_floater: bool = False


class InsuranceMatch(Contract):
    product_id: str
    provider: str
    name: str
    annual_premium_inr: float
    premium_display: str
    eligible: bool
    reasons: list[str]
    score: float


def _inr(value: float) -> str:
    from app.india.format import format_inr

    return format_inr(value)


class MatchService:
    def __init__(self, catalog: CatalogRepository):
        self._catalog = catalog

    async def match_loans(self, req: LoanMatchRequest) -> list[LoanMatch]:
        products = await self._catalog.list_by_kind("loan")
        matches: list[LoanMatch] = []
        for product in products:
            attr = product.attributes
            if attr.get("loanType") != req.loan_type:
                continue
            reasons: list[str] = []
            eligible = True

            rate = float(attr["minRate"])
            tenure = min(req.tenure_years, float(attr["maxTenureYears"]))
            if req.tenure_years > attr["maxTenureYears"]:
                reasons.append(
                    f"Tenure capped at {attr['maxTenureYears']} years by this product"
                )

            monthly_emi = emi(req.amount_inr, rate, tenure)
            foir = (monthly_emi + req.existing_emi_inr) / req.monthly_income_inr

            if req.monthly_income_inr < attr["minIncomeMonthly"]:
                eligible = False
                reasons.append(
                    f"Minimum monthly income {_inr(attr['minIncomeMonthly'])} not met"
                )
            if foir > attr["maxFoir"]:
                eligible = False
                reasons.append(
                    f"FOIR {foir:.0%} exceeds the product limit {attr['maxFoir']:.0%}"
                )
            if req.loan_type == "home" and req.property_value_inr:
                ltv = req.amount_inr / req.property_value_inr
                if ltv > attr["maxLtv"]:
                    eligible = False
                    reasons.append(
                        f"LTV {ltv:.0%} exceeds the product maximum {attr['maxLtv']:.0%}"
                    )

            processing_fee = req.amount_inr * float(attr["processingFeePct"])
            # Lower rate and lower FOIR rank higher; ineligible products sink.
            score = (1.0 - rate) * 100 + (attr["maxFoir"] - min(foir, attr["maxFoir"])) * 10
            if not eligible:
                score -= 1000
            matches.append(
                LoanMatch(
                    product_id=product.id,
                    provider=product.provider,
                    name=product.name,
                    indicative_rate=round(rate, 4),
                    emi_inr=round(monthly_emi, 2),
                    emi_display=_inr(monthly_emi),
                    processing_fee_inr=round(processing_fee, 2),
                    foir_after=round(foir, 4),
                    eligible=eligible,
                    reasons=reasons or ["Meets all eligibility criteria"],
                    score=round(score, 2),
                )
            )
        if not matches:
            raise ValidationError(f"No '{req.loan_type}' loan products in the catalog.")
        return sorted(matches, key=lambda m: m.score, reverse=True)

    async def match_insurance(self, req: InsuranceMatchRequest) -> list[InsuranceMatch]:
        products = await self._catalog.list_by_kind("insurance")
        matches: list[InsuranceMatch] = []
        for product in products:
            attr = product.attributes
            if attr.get("insuranceType") != req.insurance_type:
                continue
            reasons: list[str] = []
            eligible = True

            if not (attr["entryAgeMin"] <= req.age <= attr["entryAgeMax"]):
                eligible = False
                reasons.append(
                    f"Entry age band is {attr['entryAgeMin']} to {attr['entryAgeMax']}"
                )
            if not (attr["coverMin"] <= req.cover_inr <= attr["coverMax"]):
                eligible = False
                reasons.append(
                    f"Cover band is {_inr(attr['coverMin'])} to {_inr(attr['coverMax'])}"
                )

            lakhs = req.cover_inr / 100_000
            premium = lakhs * float(attr["annualPremiumPerLakh"])
            # Age loads premium roughly 3 percent per year over 30.
            premium *= 1 + max(0, req.age - 30) * 0.03
            if req.insurance_type == "term" and req.smoker:
                premium *= 1 + float(attr.get("smokerLoadingPct", 0))
            if req.insurance_type == "health" and req.family_floater:
                premium *= 1 - float(attr.get("familyFloaterDiscountPct", 0))

            score = -premium
            if not eligible:
                score -= 1e9
            matches.append(
                InsuranceMatch(
                    product_id=product.id,
                    provider=product.provider,
                    name=product.name,
                    annual_premium_inr=round(premium, 2),
                    premium_display=_inr(premium),
                    eligible=eligible,
                    reasons=reasons or ["Eligible for this cover and age"],
                    score=round(score, 2),
                )
            )
        if not matches:
            raise ValidationError(f"No '{req.insurance_type}' products in the catalog.")
        return sorted(matches, key=lambda m: m.score, reverse=True)
