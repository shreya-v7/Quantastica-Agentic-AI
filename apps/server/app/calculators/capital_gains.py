"""Equity capital gains (111A STCG, 112A LTCG with exemption and grandfathering).
Pure code, versioned per assessment year via the tax rule tables."""

from __future__ import annotations

from datetime import date

from pydantic import Field

from app.calculators.tax_rules import ay_2025_26
from app.schemas.base import Contract

RULES = ay_2025_26.CAPITAL_GAINS
LTCG_HOLDING_DAYS = 365


class SellLot(Contract):
    quantity: float = Field(gt=0)
    buy_price: float = Field(ge=0)
    sell_price: float = Field(ge=0)
    buy_date: str
    sell_date: str
    fmv_2018_01_31: float | None = None


class CapitalGainsResult(Contract):
    stcg: float
    ltcg: float
    ltcg_taxable: float
    stcg_tax: float
    ltcg_tax: float
    total_tax: float


def compute_equity_gains(lots: list[SellLot]) -> CapitalGainsResult:
    stcg = ltcg = 0.0
    grandfather = date.fromisoformat(RULES["ltcg_grandfather_date"])
    for lot in lots:
        bought = date.fromisoformat(lot.buy_date)
        sold = date.fromisoformat(lot.sell_date)
        cost = lot.buy_price
        if bought <= grandfather and lot.fmv_2018_01_31 is not None:
            # Grandfathering: cost is the higher of actual cost and the lower of
            # FMV on 31 Jan 2018 and the sale price.
            cost = max(lot.buy_price, min(lot.fmv_2018_01_31, lot.sell_price))
        gain = (lot.sell_price - cost) * lot.quantity
        if (sold - bought).days > LTCG_HOLDING_DAYS:
            ltcg += gain
        else:
            stcg += gain

    ltcg_taxable = max(0.0, ltcg - RULES["equity_ltcg_exemption"])
    stcg_tax = max(0.0, stcg) * RULES["equity_stcg_rate"]
    ltcg_tax = ltcg_taxable * RULES["equity_ltcg_rate"]
    return CapitalGainsResult(
        stcg=round(stcg, 2),
        ltcg=round(ltcg, 2),
        ltcg_taxable=round(ltcg_taxable, 2),
        stcg_tax=round(stcg_tax, 2),
        ltcg_tax=round(ltcg_tax, 2),
        total_tax=round(stcg_tax + ltcg_tax, 2),
    )
