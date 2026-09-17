from __future__ import annotations

from datetime import date

from pydantic import Field

from quantastica_kernel.contract import Contract


class BookLot(Contract):
    id: str
    symbol: str
    name: str
    asset_class: str
    sector: str
    quantity: float = Field(ge=0)
    cost: float = Field(ge=0)
    price: float = Field(ge=0)
    acquired_on: date
    fmv_2018: float | None = None

    @property
    def market_value(self) -> float:
        return round(self.quantity * self.price, 2)


class TaxFacts(Contract):
    basic_salary: float = Field(ge=0)
    hra_received: float = Field(default=0, ge=0)
    other_income: float = Field(default=0, ge=0)
    rent_paid: float = Field(default=0, ge=0)
    metro_city: bool = True
    deduction_80c: float = Field(default=0, ge=0)
    health_premium_self: float = Field(default=0, ge=0)
    nps_80ccd_1b: float = Field(default=0, ge=0)
    home_loan_interest: float = Field(default=0, ge=0)
    assessment_year: str = "2025-26"


class BookSnapshot(Contract):
    household_id: str
    household_name: str
    as_of: date
    lots: list[BookLot]
    tax: TaxFacts | None = None

    @property
    def total_market(self) -> float:
        return round(sum(lot.market_value for lot in self.lots), 2)
