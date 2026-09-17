"""Temporal corrections, audit stability, concurrent writes and persisted outbox."""
import asyncio
from copy import deepcopy
from datetime import UTC, datetime, timedelta

import pytest
from app.exceptions.fixtures import mehta_book
from app.infra.repo.book_repo import BookRepository
from quantastica_kernel.sim import SimulatedClock, SimulatedRNG

VALID = datetime(2026, 9, 16, tzinfo=UTC)
RECORDED = datetime(2026, 9, 17, tzinfo=UTC)


async def test_two_axes_and_backdated_correction(container):
    repo = BookRepository(container.session_factory, clock=lambda: RECORDED)
    book = mehta_book()
    lot = book.lots[0]
    await repo.seed_snapshot(book)
    baseline = await repo.history(book.household_id)
    await repo.mutate_lot_quantity(book.household_id, lot.id, 100, VALID + timedelta(days=2))
    middle = await repo.history(book.household_id)
    await repo.mutate_lot_quantity(book.household_id, lot.id, 50, VALID + timedelta(days=1))
    history = await repo.history(book.household_id)
    assert baseline == history[:1]
    assert middle == history[:2]
    assert all(a['recorded_time'] < b['recorded_time'] for a, b in zip(history, history[1:], strict=False))
    async def quantity(valid, recorded):
        state = await repo.as_of(book.household_id, valid, recorded)
        return next(row.quantity for row in state.lots if row.id == lot.id)
    assert await quantity(VALID + timedelta(days=1), baseline[0]['recorded_time']) == lot.quantity
    assert await quantity(VALID + timedelta(days=1), history[-1]['recorded_time']) == 50
    assert await quantity(VALID + timedelta(days=3), history[-1]['recorded_time']) == 100
    assert await repo.as_of(book.household_id, VALID - timedelta(days=1), RECORDED) is None
    assert len(await repo.pending_outbox()) == 3


async def test_concurrency_and_idempotency(container):
    repo = BookRepository(container.session_factory, clock=lambda: RECORDED)
    book = mehta_book()
    await repo.seed_snapshot(book)
    await asyncio.gather(*(repo.mutate_lot_quantity(book.household_id, book.lots[0].id, n)
                           for n in range(1, 9)))
    history = await repo.history(book.household_id)
    assert [r['seq'] for r in history] == list(range(1, 10))
    assert len({r['recorded_time'] for r in history}) == 9
    await repo.mutate_lot_quantity(book.household_id, book.lots[0].id, 12,
                                  idempotency_key='same')
    await repo.mutate_lot_quantity(book.household_id, book.lots[0].id, 12,
                                  idempotency_key='same')
    assert len(await repo.history(book.household_id)) == 10
    with pytest.raises(ValueError, match='Idempotency'):
        await repo.mutate_lot_quantity(book.household_id, book.lots[0].id, 13,
                                      idempotency_key='same')


async def test_seed_ingest_and_naive_query(container):
    repo = BookRepository(container.session_factory, clock=lambda: RECORDED)
    book = mehta_book()
    await repo.seed_snapshot(book)
    await repo.seed_snapshot(book)
    assert len(await repo.history(book.household_id)) == 1
    changed = book.model_copy(deep=True)
    changed.tax.basic_salary = 4_000_000
    await repo.seed_snapshot(changed)
    history = await repo.history(book.household_id)
    earlier = await repo.as_of(book.household_id, VALID, history[0]['recorded_time'])
    later = await repo.as_of(book.household_id, VALID, history[-1]['recorded_time'])
    assert earlier.tax.basic_salary == 3_600_000
    assert later.tax.basic_salary == 4_000_000
    with pytest.raises(ValueError, match='timezone'):
        await repo.as_of(book.household_id, datetime(2026, 9, 17), RECORDED)


async def test_recorded_time_never_rewritten_property(container):
    rng = SimulatedRNG(11)
    clock = SimulatedClock(RECORDED)
    repo = BookRepository(container.session_factory, clock=clock)
    book = mehta_book()
    await repo.seed_snapshot(book)
    prefixes = [deepcopy(await repo.history(book.household_id))]
    lot_id = book.lots[0].id
    for _ in range(16):
        clock.advance(timedelta(seconds=1))
        valid = VALID + timedelta(days=rng.randint(0, 8))
        await repo.mutate_lot_quantity(
            book.household_id, lot_id, rng.randint(1, 400), valid)
        history = await repo.history(book.household_id)
        assert all(
            a["recorded_time"] < b["recorded_time"]
            for a, b in zip(history, history[1:], strict=False)
        )
        for prefix in prefixes:
            assert history[:len(prefix)] == prefix
        prefixes.append(deepcopy(history))
        latest = await repo.as_of(
            book.household_id, datetime.max.replace(tzinfo=UTC), clock.now())
        assert latest is not None


async def test_as_of_route(client):
    listed = (await client.get("/api/desk/households")).json()
    assert listed["ok"] is True
    household_id = listed["data"][0]["id"]
    history = (await client.get(f"/api/desk/households/{household_id}/history")).json()
    assert history["ok"] is True
    assert history["data"]
    first = history["data"][0]
    as_of = await client.get(
        f"/api/desk/households/{household_id}/as-of",
        params={"valid_time": first["valid_time"], "recorded_time": first["recorded_time"]},
    )
    assert as_of.status_code == 200
    body = as_of.json()
    assert body["ok"] is True
    assert body["data"]["householdId"] == household_id
    naive = await client.get(
        f"/api/desk/households/{household_id}/as-of",
        params={"valid_time": "2026-09-16T00:00:00", "recorded_time": first["recorded_time"]},
    )
    assert naive.status_code == 422
