"""Northstar demo books. Same holdings as the mock bank, plus lot dates and tax facts.

as_of is frozen at 2026-09-16 so lot_clock stay stable in tests and demos.
"""

from __future__ import annotations

from datetime import date

from app.exceptions.snapshot import BookLot, BookSnapshot, TaxFacts
from app.providers.bank.mock import _HOLDINGS

AS_OF = date(2026, 9, 16)

_MEHTA_ACQUIRED = {
    "RELIANCE.NS": date(2020, 1, 15),
    "TCS.NS": date(2025, 10, 20),
    "INFY.NS": date(2024, 1, 10),
    "HDFCBANK.NS": date(2023, 6, 1),
    "NIFTYBEES.NS": date(2024, 8, 1),
    "LIQUIDBEES.NS": date(2025, 1, 1),
}

_RAO_ACQUIRED = {
    "NIFTYBEES.NS": date(2024, 8, 1),
    "RELIANCE.NS": date(2023, 3, 1),
}


def _lots(customer_id: str, acquired: dict[str, date]) -> list[BookLot]:
    lots: list[BookLot] = []
    for index, row in enumerate(_HOLDINGS[customer_id], start=1):
        symbol = str(row["symbol"])
        lots.append(
            BookLot(
                id=f"lot_{customer_id}_{index}",
                symbol=symbol,
                name=str(row["name"]),
                asset_class=str(row["assetClass"]),
                sector=str(row["sector"]),
                quantity=float(row["quantity"]),
                cost=float(row["costBasis"]),
                price=float(row["priceInr"]),
                acquired_on=acquired[symbol],
            )
        )
    return lots


def mehta_book() -> BookSnapshot:
    return BookSnapshot(
        household_id="hh_mehta",
        household_name="Karan Mehta",
        as_of=AS_OF,
        lots=_lots("cust_hni_mehta", _MEHTA_ACQUIRED),
        tax=TaxFacts(
            basic_salary=3_600_000,
            deduction_80c=50_000,
            metro_city=True,
        ),
    )


def rao_book() -> BookSnapshot:
    return BookSnapshot(
        household_id="hh_rao",
        household_name="Ananya Rao",
        as_of=AS_OF,
        lots=_lots("cust_affluent_rao", _RAO_ACQUIRED),
        tax=TaxFacts(
            basic_salary=1_200_000,
            deduction_80c=150_000,
            nps_80ccd_1b=50_000,
            metro_city=True,
        ),
    )


def demo_books() -> list[BookSnapshot]:
    return [mehta_book(), rao_book()]
