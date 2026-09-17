"""Exception rules. Each rule is a pure function over a BookSnapshot."""

from __future__ import annotations

from datetime import date, timedelta
from hashlib import sha256

from quantastica_kernel.calculators.capital_gains import (
    LTCG_HOLDING_DAYS,
    SellLot,
    compute_equity_gains,
)
from quantastica_kernel.calculators.tax import TaxInput, compare_regimes
from quantastica_kernel.calculators.tax_rules.ay_2025_26 import DEDUCTION_CAPS
from quantastica_kernel.exceptions.hits import ExceptionHit, PolicyTable
from quantastica_kernel.exceptions.snapshot import BookSnapshot


def _fp(*parts: str) -> str:
    raw = "|".join(parts)
    return sha256(raw.encode()).hexdigest()[:16]


def regime_watch(book: BookSnapshot, policy: PolicyTable) -> list[ExceptionHit]:
    if book.tax is None:
        return []
    tax = book.tax
    payload = TaxInput(
        assessment_year=tax.assessment_year,
        basic_salary=tax.basic_salary,
        hra_received=tax.hra_received,
        other_income=tax.other_income,
        rent_paid=tax.rent_paid,
        metro_city=tax.metro_city,
        deduction_80c=tax.deduction_80c,
        health_premium_self=tax.health_premium_self,
        nps_80ccd_1b=tax.nps_80ccd_1b,
        home_loan_interest=tax.home_loan_interest,
    )
    comparison = compare_regimes(payload)
    if comparison.saving_inr < policy.regime_saving_threshold:
        return []
    cheaper = comparison.recommended
    other = "old" if cheaper == "new" else "new"
    return [
        ExceptionHit(
            rule_id="regime_watch",
            version="1",
            title=f"{cheaper} regime is cheaper by Rs {comparison.saving_inr:,.0f}",
            rupee_delta=comparison.saving_inr,
            due_date=None,
            severity="high" if comparison.saving_inr >= 100_000 else "medium",
            metric_ids=["tax.saving_inr", "tax.recommended"],
            fingerprint=_fp("regime_watch", book.household_id, cheaper),
            calculator="compare_regimes",
            inputs=payload.model_dump(mode="json"),
            outputs={
                "recommended": cheaper,
                "other": other,
                "savingInr": comparison.saving_inr,
                "oldTotalTax": comparison.old_regime.total_tax,
                "newTotalTax": comparison.new_regime.total_tax,
            },
        )
    ]


def lot_clock(book: BookSnapshot, policy: PolicyTable) -> list[ExceptionHit]:
    hits: list[ExceptionHit] = []
    for lot in book.lots:
        if lot.asset_class not in {"equity", "etf"}:
            continue
        if lot.quantity <= 0:
            continue
        held = (book.as_of - lot.acquired_on).days
        remaining = LTCG_HOLDING_DAYS - held
        if remaining <= 0 or remaining > policy.lot_clock_days:
            continue
        boundary = lot.acquired_on + timedelta(days=LTCG_HOLDING_DAYS + 1)
        today_lot = SellLot(
            quantity=lot.quantity,
            buy_price=lot.cost,
            sell_price=lot.price,
            buy_date=lot.acquired_on.isoformat(),
            sell_date=book.as_of.isoformat(),
            fmv_2018_01_31=lot.fmv_2018,
        )
        later_lot = today_lot.model_copy(update={"sell_date": boundary.isoformat()})
        now_tax = compute_equity_gains([today_lot])
        later_tax = compute_equity_gains([later_lot])
        extra = round(now_tax.total_tax - later_tax.total_tax, 2)
        if extra <= 0:
            continue
        hits.append(
            ExceptionHit(
                rule_id="lot_clock",
                version="1",
                title=(
                    f"{lot.symbol} turns LTCG on {boundary.isoformat()} "
                    f"({remaining} days). Selling today costs Rs {extra:,.0f} more."
                ),
                rupee_delta=extra,
                due_date=boundary,
                severity="high" if remaining <= 14 else "medium",
                metric_ids=["cg.stcg_tax", "cg.ltcg_tax", "cg.total_tax"],
                fingerprint=_fp("lot_clock", lot.id),
                calculator="compute_equity_gains",
                inputs={
                    "lotId": lot.id,
                    "symbol": lot.symbol,
                    "quantity": lot.quantity,
                    "cost": lot.cost,
                    "price": lot.price,
                    "acquiredOn": lot.acquired_on.isoformat(),
                    "asOf": book.as_of.isoformat(),
                    "boundary": boundary.isoformat(),
                },
                outputs={
                    "daysHeld": held,
                    "daysRemaining": remaining,
                    "taxIfSoldToday": now_tax.total_tax,
                    "taxIfSoldAfter": later_tax.total_tax,
                    "extraTaxToday": extra,
                    "stcgToday": now_tax.stcg_tax,
                    "ltcgAfter": later_tax.ltcg_tax,
                },
            )
        )
    return hits


def concentration_tripwire(book: BookSnapshot, policy: PolicyTable) -> list[ExceptionHit]:
    total = book.total_market
    if total <= 0:
        return []
    hits: list[ExceptionHit] = []
    by_name: dict[str, float] = {}
    by_sector: dict[str, float] = {}
    for lot in book.lots:
        by_name[lot.symbol] = by_name.get(lot.symbol, 0.0) + lot.market_value
        by_sector[lot.sector] = by_sector.get(lot.sector, 0.0) + lot.market_value

    for symbol, value in by_name.items():
        weight = value / total
        if weight <= policy.name_cap:
            continue
        excess = round((weight - policy.name_cap) * total, 2)
        hits.append(
            ExceptionHit(
                rule_id="concentration_tripwire",
                version="1",
                title=(
                    f"{symbol} is {weight:.1%} of the book "
                    f"(cap {policy.name_cap:.0%}). Excess Rs {excess:,.0f}."
                ),
                rupee_delta=excess,
                due_date=None,
                severity="high" if weight >= policy.name_cap * 2 else "medium",
                metric_ids=["risk.name_weight", "risk.name_excess_inr"],
                fingerprint=_fp("concentration_tripwire", "name", symbol),
                calculator="weights",
                calculator_version="book_v1",
                inputs={
                    "symbol": symbol,
                    "marketValue": value,
                    "totalMarket": total,
                    "nameCap": policy.name_cap,
                },
                outputs={"weight": round(weight, 6), "excessInr": excess},
            )
        )

    for sector, value in by_sector.items():
        weight = value / total
        if weight <= policy.sector_cap:
            continue
        excess = round((weight - policy.sector_cap) * total, 2)
        hits.append(
            ExceptionHit(
                rule_id="concentration_tripwire",
                version="1",
                title=(
                    f"{sector} is {weight:.1%} of the book "
                    f"(cap {policy.sector_cap:.0%}). Excess Rs {excess:,.0f}."
                ),
                rupee_delta=excess,
                due_date=None,
                severity="medium",
                metric_ids=["risk.sector_weight", "risk.sector_excess_inr"],
                fingerprint=_fp("concentration_tripwire", "sector", sector),
                calculator="weights",
                calculator_version="book_v1",
                inputs={
                    "sector": sector,
                    "marketValue": value,
                    "totalMarket": total,
                    "sectorCap": policy.sector_cap,
                },
                outputs={"weight": round(weight, 6), "excessInr": excess},
            )
        )
    return hits


def deduction_headroom(book: BookSnapshot, policy: PolicyTable) -> list[ExceptionHit]:
    if book.tax is None:
        return []
    tax = book.tax
    comparison = compare_regimes(
        TaxInput(
            assessment_year=tax.assessment_year,
            basic_salary=tax.basic_salary,
            hra_received=tax.hra_received,
            other_income=tax.other_income,
            rent_paid=tax.rent_paid,
            metro_city=tax.metro_city,
            deduction_80c=tax.deduction_80c,
            health_premium_self=tax.health_premium_self,
            nps_80ccd_1b=tax.nps_80ccd_1b,
            home_loan_interest=tax.home_loan_interest,
        )
    )
    if comparison.recommended == "new":
        return []
    unused_80c = max(0.0, DEDUCTION_CAPS["80c"] - tax.deduction_80c)
    unused_nps = max(0.0, DEDUCTION_CAPS["80ccd_1b"] - tax.nps_80ccd_1b)
    unused = round(unused_80c + unused_nps, 2)
    if unused < policy.deduction_unused_threshold:
        return []
    return [
        ExceptionHit(
            rule_id="deduction_headroom",
            version="1",
            title=(
                f"Unused old-regime deductions Rs {unused:,.0f} "
                f"(80C Rs {unused_80c:,.0f}, 80CCD(1B) Rs {unused_nps:,.0f})."
            ),
            rupee_delta=unused,
            due_date=date(int(tax.assessment_year[:4]) + 1, 3, 31),
            severity="low",
            metric_ids=["tax.unused_80c", "tax.unused_80ccd_1b"],
            fingerprint=_fp("deduction_headroom", book.household_id),
            calculator="compare_regimes",
            inputs=tax.model_dump(mode="json"),
            outputs={
                "unused80c": unused_80c,
                "unused80ccd1b": unused_nps,
                "recommended": comparison.recommended,
            },
        )
    ]


def ais_mismatch(_book: BookSnapshot, _policy: PolicyTable) -> list[ExceptionHit]:
    """Stub until Phase 2 AIS ingest. Always empty."""
    return []


RULES = (
    regime_watch,
    lot_clock,
    concentration_tripwire,
    deduction_headroom,
    ais_mismatch,
)
