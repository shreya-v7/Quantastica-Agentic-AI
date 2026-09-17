"""Golden exception sets for the Northstar Mehta book. No LLM. No Docker."""

from __future__ import annotations

from datetime import timedelta

from app.calculators.capital_gains import LTCG_HOLDING_DAYS, SellLot, compute_equity_gains
from app.calculators.tax import TaxInput, compare_regimes
from app.exceptions.engine import compute_exceptions, diff_exceptions
from app.exceptions.fixtures import mehta_book
from app.exceptions.hits import PolicyTable


def test_mehta_fires_concentration_and_lot_clock():
    hits = compute_exceptions(mehta_book())
    rules = {hit.rule_id for hit in hits}
    assert "concentration_tripwire" in rules
    assert "lot_clock" in rules
    assert "regime_watch" in rules
    assert all(hit.rule_id != "ais_mismatch" for hit in hits)
    assert len(hits) >= 2


def test_mehta_reliance_excess_matches_weights():
    book = mehta_book()
    policy = PolicyTable()
    total = book.total_market
    reliance = next(lot for lot in book.lots if lot.symbol == "RELIANCE.NS")
    expected = round(reliance.market_value - policy.name_cap * total, 2)
    hit = next(
        h
        for h in compute_exceptions(book, policy)
        if h.rule_id == "concentration_tripwire" and h.inputs.get("symbol") == "RELIANCE.NS"
    )
    assert hit.rupee_delta == expected
    assert hit.calculator == "weights"


def test_mehta_tcs_lot_clock_matches_capital_gains():
    book = mehta_book()
    lot = next(row for row in book.lots if row.symbol == "TCS.NS")
    remaining = LTCG_HOLDING_DAYS - (book.as_of - lot.acquired_on).days
    assert 0 < remaining <= 60
    boundary = lot.acquired_on + timedelta(days=LTCG_HOLDING_DAYS + 1)
    today = compute_equity_gains(
        [
            SellLot(
                quantity=lot.quantity,
                buy_price=lot.cost,
                sell_price=lot.price,
                buy_date=lot.acquired_on.isoformat(),
                sell_date=book.as_of.isoformat(),
            )
        ]
    )
    later = compute_equity_gains(
        [
            SellLot(
                quantity=lot.quantity,
                buy_price=lot.cost,
                sell_price=lot.price,
                buy_date=lot.acquired_on.isoformat(),
                sell_date=boundary.isoformat(),
            )
        ]
    )
    expected = round(today.total_tax - later.total_tax, 2)
    hit = next(h for h in compute_exceptions(book) if h.rule_id == "lot_clock")
    assert hit.rupee_delta == expected
    assert hit.due_date == boundary


def test_mehta_regime_saving_matches_calculator():
    book = mehta_book()
    assert book.tax is not None
    tax = book.tax
    comparison = compare_regimes(
        TaxInput(
            basic_salary=tax.basic_salary,
            deduction_80c=tax.deduction_80c,
            metro_city=tax.metro_city,
        )
    )
    hit = next(h for h in compute_exceptions(book) if h.rule_id == "regime_watch")
    assert hit.rupee_delta == comparison.saving_inr
    assert hit.outputs["recommended"] == comparison.recommended


def test_new_regime_suppresses_deduction_headroom():
    hits = compute_exceptions(mehta_book())
    assert all(h.rule_id != "deduction_headroom" for h in hits)


def test_holding_mutation_changes_concentration_diff():
    book = mehta_book()
    before = compute_exceptions(book)
    lots = []
    for lot in book.lots:
        if lot.symbol == "RELIANCE.NS":
            lots.append(lot.model_copy(update={"quantity": lot.quantity * 2}))
        else:
            lots.append(lot)
    after_book = book.model_copy(update={"lots": lots})
    after = compute_exceptions(after_book)
    diff = diff_exceptions(before, after)
    assert diff["changed"] or diff["added"]
    rel_before = next(
        h for h in before if h.inputs.get("symbol") == "RELIANCE.NS"
    )
    rel_after = next(h for h in after if h.inputs.get("symbol") == "RELIANCE.NS")
    assert rel_after.rupee_delta > rel_before.rupee_delta
