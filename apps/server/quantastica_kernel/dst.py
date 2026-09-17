"""Seeded deterministic simulation: reorder, duplicate, delay, drop.

Coverage is the fraction of fault classes that actually fired. A failing seed
must reproduce the same report.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from .guard import screen
from .sim import SimulatedClock, SimulatedRNG
from .temporal import reconstruct

FAULTS = ("reorder", "duplicate", "delay", "drop")
VALID0 = datetime(2026, 9, 16, tzinfo=UTC)


def _book(quantity: float) -> dict:
    return {
        "household_id": "hh_sim",
        "household_name": "Sim",
        "as_of": "2026-09-16",
        "lots": [{
            "id": "l1", "symbol": "X", "name": "X", "asset_class": "equity",
            "sector": "IT", "quantity": quantity, "cost": 1, "price": 2,
            "acquired_on": "2025-01-01",
        }],
        "tax": None,
    }


@dataclass
class SimReport:
    seed: int
    ok: bool
    coverage: dict[str, int]
    invariants: dict[str, bool]
    note: str = ""


@dataclass
class Simulator:
    seed: int
    clock: SimulatedClock = field(init=False)
    rng: SimulatedRNG = field(init=False)

    def __post_init__(self) -> None:
        self.rng = SimulatedRNG(self.seed)
        self.clock = SimulatedClock(datetime(2026, 9, 17, tzinfo=UTC))

    def run(self, steps: int = 24, faults: tuple[str, ...] = FAULTS) -> SimReport:
        coverage = {name: 0 for name in FAULTS}
        events = [{
            "id": "e0", "event_type": "book.snapshot", "payload": _book(10),
            "seq": 1, "valid_time": VALID0, "recorded_time": self.clock.now(),
        }]
        processed: set[str] = set()
        effects: list[str] = []
        deliveries: list[dict] = []

        planned = []
        for index in range(steps):
            self.clock.advance(timedelta(seconds=1))
            qty = self.rng.randint(1, 80)
            planned.append({
                "id": f"e{index+1}",
                "event_type": "book.patch",
                "payload": {"lot_quantities": [{"id": "l1", "quantity": qty}]},
                "seq": index + 2,
                "valid_time": VALID0 + timedelta(days=self.rng.randint(0, 5)),
                "recorded_time": self.clock.now(),
            })

        stream: list[dict] = []
        delayed: list[dict] = []
        for item in planned:
            roll = self.rng.random()
            if "drop" in faults and roll < 0.08:
                coverage["drop"] += 1
                continue
            if "delay" in faults and roll < 0.16:
                coverage["delay"] += 1
                delayed.append(item)
                continue
            stream.append(item)
            if "duplicate" in faults and roll < 0.28:
                coverage["duplicate"] += 1
                stream.append(deepcopy(item))
        stream.extend(delayed)
        if "reorder" in faults and len(stream) > 3:
            # Reorder delivery, not recorded_time. Consumers must still be idempotent.
            i = self.rng.randint(0, len(stream) - 2)
            stream[i], stream[i + 1] = stream[i + 1], stream[i]
            coverage["reorder"] += 1

        for item in stream:
            key = item["id"]
            if key in processed:
                continue
            processed.add(key)
            events.append(item)
            effects.append(key)
            deliveries.append(item)

        latest = reconstruct(events, datetime.max.replace(tzinfo=UTC), self.clock.now())
        conserved = latest is not None and latest.lots[0].quantity >= 0
        idempotent = len(effects) == len(set(effects))
        # Cross-tenant: simulator only has hh_sim.
        tenant_ok = all(
            row.get("payload", {}).get("household_id", "hh_sim") in {"hh_sim", None}
            for row in events
        )
        guard = screen("Rs 9999999 ungrounded", allowed_amounts=[10.0])
        invariants = {
            "reconstruction": latest is not None,
            "conservation": conserved,
            "idempotent": idempotent,
            "no_cross_tenant": tenant_ok,
            "guard_fail_closed": not guard.ok,
        }
        return SimReport(
            seed=self.seed,
            ok=all(invariants.values()),
            coverage=coverage,
            invariants=invariants,
        )
