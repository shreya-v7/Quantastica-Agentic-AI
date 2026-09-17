"""Pure bitemporal reconstruction. No database."""
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from unittest import TestCase

from quantastica_kernel.sim import SimulatedClock, SimulatedRNG
from quantastica_kernel.temporal import instant, reconstruct, snapshot_patch

VALID = datetime(2026, 9, 16, tzinfo=UTC)
RECORDED = datetime(2026, 9, 17, tzinfo=UTC)

BOOK = {
    "household_id": "hh", "household_name": "Test", "as_of": "2026-09-16",
    "lots": [{"id": "l1", "symbol": "X", "name": "X", "asset_class": "equity",
              "sector": "IT", "quantity": 10, "cost": 1, "price": 2,
              "acquired_on": "2025-01-01"}],
    "tax": None,
}


def _event(seq, valid, recorded, etype, payload):
    return {"id": f"e{seq}", "event_type": etype, "payload": payload, "seq": seq,
            "valid_time": valid, "recorded_time": recorded}


class TemporalTests(TestCase):
    def test_as_of_both_axes_and_backdated_correction(self):
        events = [
            _event(1, VALID, RECORDED, "book.snapshot", deepcopy(BOOK)),
            _event(2, VALID + timedelta(days=2), RECORDED + timedelta(seconds=1),
                   "book.patch", {"lot_quantities": [{"id": "l1", "quantity": 100}]}),
            _event(3, VALID + timedelta(days=1), RECORDED + timedelta(seconds=2),
                   "book.patch", {"lot_quantities": [{"id": "l1", "quantity": 50}]}),
        ]

        def qty(valid, recorded):
            state = reconstruct(events, valid, recorded)
            return next(lot.quantity for lot in state.lots)

        self.assertEqual(qty(VALID + timedelta(days=1), RECORDED), 10)
        self.assertEqual(qty(VALID + timedelta(days=1), events[-1]["recorded_time"]), 50)
        self.assertEqual(qty(VALID + timedelta(days=3), events[-1]["recorded_time"]), 100)
        self.assertIsNone(reconstruct(events, VALID - timedelta(days=1), RECORDED))

    def test_audit_stability_and_naive_time_rejected(self):
        events = [_event(1, VALID, RECORDED, "book.snapshot", deepcopy(BOOK))]
        before = reconstruct(events, VALID, RECORDED)
        events.append(_event(
            2, VALID, RECORDED + timedelta(seconds=1), "book.patch",
            {"lot_quantities": [{"id": "l1", "quantity": 99}]},
        ))
        self.assertEqual(reconstruct(events, VALID, RECORDED), before)
        with self.assertRaises(ValueError):
            reconstruct(events, datetime(2026, 9, 16), RECORDED)
        with self.assertRaises(ValueError):
            instant("2026-09-16T00:00:00")

    def test_recorded_time_property_append_only(self):
        rng = SimulatedRNG(7)
        clock = SimulatedClock(RECORDED)
        log = [_event(1, VALID, clock.now(), "book.snapshot", deepcopy(BOOK))]
        prefixes = [deepcopy(log)]
        for step in range(40):
            clock.advance(timedelta(seconds=1))
            valid = VALID + timedelta(days=rng.randint(0, 12))
            log.append(_event(
                step + 2, valid, clock.now(), "book.patch",
                {"lot_quantities": [{"id": "l1", "quantity": rng.randint(1, 500)}]},
            ))
            self.assertTrue(all(
                a["recorded_time"] < b["recorded_time"] for a, b in zip(log, log[1:], strict=False)
            ))
            for prefix in prefixes:
                self.assertEqual(log[:len(prefix)], prefix)
            prefixes.append(deepcopy(log))
            self.assertIsNotNone(reconstruct(
                log, datetime.max.replace(tzinfo=UTC), clock.now()))

    def test_snapshot_patch_round_trip(self):
        first = reconstruct(
            [_event(1, VALID, RECORDED, "book.snapshot", deepcopy(BOOK))], VALID, RECORDED)
        after = first.model_copy(deep=True)
        after.lots[0].quantity = 3
        after.household_name = "Renamed"
        patch = snapshot_patch(first, after)
        rebuilt = reconstruct([
            _event(1, VALID, RECORDED, "book.snapshot", deepcopy(BOOK)),
            _event(2, VALID, RECORDED + timedelta(seconds=1), "book.patch", patch),
        ], VALID, RECORDED + timedelta(seconds=1))
        self.assertEqual(rebuilt, after)
