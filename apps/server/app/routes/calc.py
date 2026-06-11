"""Deterministic calculator endpoints (Phase C). The calculator decides; the LLM only
explains. Every response is INR."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import Field

from app.calculators.capital_gains import CapitalGainsResult, SellLot, compute_equity_gains
from app.calculators.planning import (
    AffordabilityInput,
    SimulationResult,
    affordability,
    monte_carlo_sip,
    required_monthly_sip,
    step_up_sip_first_month,
)
from app.calculators.tax import TaxInput, compare_regimes
from app.core.dependencies import current_user_id
from app.core.envelope import success
from app.india.format import format_inr, format_inr_compact
from app.schemas.base import Contract

router = APIRouter()


@router.post("/tax/compare")
async def tax_compare(body: TaxInput, _: str = Depends(current_user_id)) -> dict:
    result = compare_regimes(body)
    payload = result.model_dump(by_alias=True)
    payload["savingDisplay"] = format_inr_compact(result.saving_inr)
    return success(payload)


class CapitalGainsRequest(Contract):
    lots: list[SellLot] = Field(min_length=1)


@router.post("/tax/capital-gains")
async def capital_gains(body: CapitalGainsRequest, _: str = Depends(current_user_id)) -> dict:
    result: CapitalGainsResult = compute_equity_gains(body.lots)
    return success(result)


class SipRequest(Contract):
    target_inr: float = Field(gt=0)
    years: float = Field(gt=0)
    annual_return: float = Field(default=0.12, gt=0, lt=1)
    annual_step_up: float = Field(default=0.0, ge=0, lt=1)


@router.post("/calc/sip")
async def sip(body: SipRequest, _: str = Depends(current_user_id)) -> dict:
    flat = required_monthly_sip(body.target_inr, body.years, body.annual_return)
    payload = {
        "targetInr": body.target_inr,
        "targetDisplay": format_inr_compact(body.target_inr),
        "monthlySip": round(flat, 2),
        "monthlySipDisplay": format_inr(flat),
    }
    if body.annual_step_up > 0:
        step = step_up_sip_first_month(
            body.target_inr, body.years, body.annual_return, body.annual_step_up
        )
        payload["stepUpFirstMonthSip"] = round(step, 2)
        payload["stepUpFirstMonthSipDisplay"] = format_inr(step)
    return success(payload)


@router.post("/calc/affordability")
async def calc_affordability(
    body: AffordabilityInput, _: str = Depends(current_user_id)
) -> dict:
    return success(affordability(body))


class SimulateRequest(Contract):
    monthly_sip: float = Field(gt=0)
    years: float = Field(gt=0)
    annual_return: float = Field(default=0.12, gt=0, lt=1)
    annual_volatility: float = Field(default=0.18, gt=0, lt=1)


@router.post("/simulate")
async def simulate(body: SimulateRequest, _: str = Depends(current_user_id)) -> dict:
    result: SimulationResult = monte_carlo_sip(
        body.monthly_sip, body.years, body.annual_return, body.annual_volatility
    )
    payload = result.model_dump(by_alias=True)
    payload["bandsDisplay"] = {
        "p10": format_inr_compact(result.p10),
        "p50": format_inr_compact(result.p50),
        "p90": format_inr_compact(result.p90),
    }
    return success(payload)
