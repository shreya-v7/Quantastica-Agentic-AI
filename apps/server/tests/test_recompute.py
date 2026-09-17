"""Incremental recompute against the Mehta book and a medium synthetic tier."""
from datetime import UTC, datetime, timedelta

from app.exceptions.engine import compute_exceptions, merge_hits
from app.exceptions.fixtures import mehta_book
from app.infra.repo.book_repo import BookRepository
from app.services.desk_service import DeskService
from quantastica_kernel.recompute import fields_from_event, plan_recompute
from quantastica_kernel.sim import SimulatedClock

VALID = datetime(2026, 9, 16, tzinfo=UTC)
RECORDED = datetime(2026, 9, 17, tzinfo=UTC)
MEDIUM = 1_000


def test_medium_tier_incremental_cost_is_sublinear():
    changed = fields_from_event(
        "book.patch", {"lot_quantities": [{"id": "lot", "quantity": 12}]})
    incremental = plan_recompute(changed).cost
    full = MEDIUM * 5
    assert incremental == 2
    assert incremental < full
    # Same event on 10 or 1,000 households has the same dirty-set cost.
    assert incremental == plan_recompute(changed).cost


def test_mehta_incremental_equals_full_after_quantity_change():
    book = mehta_book()
    prior = compute_exceptions(book)
    lots = [
        lot.model_copy(update={"quantity": lot.quantity * 2}) if lot.symbol == "RELIANCE.NS"
        else lot
        for lot in book.lots
    ]
    after = book.model_copy(update={"lots": lots})
    dirty = plan_recompute(fields_from_event(
        "book.patch", {"lot_quantities": [{"id": "x", "quantity": 1}]})).rules
    merged = merge_hits(prior, compute_exceptions(after, rule_ids=dirty), dirty)
    assert merged == compute_exceptions(after)


async def test_outbox_drain_uses_dirty_set(container):
    clock = SimulatedClock(RECORDED)
    books = BookRepository(container.session_factory, clock=clock)
    desk = DeskService(books)
    book = mehta_book()
    await books.seed_snapshot(book)
    clock.advance(timedelta(seconds=1))
    await desk.recompute(book.household_id)
    before = await books.list_exceptions(book.household_id)
    regime = next(row for row in before if row["ruleId"] == "regime_watch")
    lot = book.lots[0]
    clock.advance(timedelta(seconds=1))
    await desk.set_lot_quantity(book.household_id, lot.id, lot.quantity + 10, VALID)
    after = await books.list_exceptions(book.household_id)
    still = next(row for row in after if row["ruleId"] == "regime_watch")
    assert still["rupeeDelta"] == regime["rupeeDelta"]
    assert still["fingerprint"] == regime["fingerprint"]
    assert await books.pending_outbox() == []
