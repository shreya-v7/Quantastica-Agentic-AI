"""Minimal async circuit breaker for outbound dependencies.

After `failure_threshold` consecutive failures the breaker opens and fast-fails calls
for `reset_seconds`, sparing a struggling upstream and returning a typed error quickly.
The first call after the cooldown is allowed through (half-open); success closes the
breaker, another failure reopens it.
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import TypeVar

from app.core.errors import ProviderUnavailableError

T = TypeVar("T")


class CircuitBreaker:
    def __init__(self, name: str, failure_threshold: int = 5, reset_seconds: float = 30.0):
        self._name = name
        self._threshold = failure_threshold
        self._reset = reset_seconds
        self._failures = 0
        self._opened_at: float | None = None

    @property
    def is_open(self) -> bool:
        if self._opened_at is None:
            return False
        # Once the cooldown elapses the breaker reports closed to allow a half-open trial.
        return time.monotonic() - self._opened_at < self._reset

    async def call(self, fn: Callable[[], Awaitable[T]]) -> T:
        if self.is_open:
            raise ProviderUnavailableError(
                self._name, "circuit open after repeated failures; retry shortly"
            )
        try:
            result = await fn()
        except Exception:
            self._failures += 1
            if self._failures >= self._threshold:
                self._opened_at = time.monotonic()
            raise
        self._failures = 0
        self._opened_at = None
        return result
