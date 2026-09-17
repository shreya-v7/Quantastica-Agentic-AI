"""Determinism seams for later simulation testing.

Clock and RNG are injected. Network and disk stay at the application edge.
The kernel itself still has no wall clock and no global random state.
"""
from __future__ import annotations

import random
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from .temporal import instant

Clock = Callable[[], datetime]


def utc_now() -> datetime:
    return datetime.now(UTC)


class SimulatedClock:
    """Synthetic time. Advance is explicit so a seed can replay the same instants."""

    def __init__(self, start: datetime):
        self._now = instant(start)

    def now(self) -> datetime:
        return self._now

    def advance(self, delta: timedelta) -> datetime:
        if delta <= timedelta(0):
            raise ValueError("Clock must advance forward")
        self._now = self._now + delta
        return self._now

    def tick(self) -> datetime:
        return self.advance(timedelta(microseconds=1))

    def __call__(self) -> datetime:
        return self.now()


class SimulatedRNG:
    """Private RNG. Callers that need chance must take this, not the global module."""

    def __init__(self, seed: int):
        self._rng = random.Random(seed)

    def randint(self, lo: int, hi: int) -> int:
        return self._rng.randint(lo, hi)

    def random(self) -> float:
        return self._rng.random()
