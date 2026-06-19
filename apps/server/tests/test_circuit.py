"""Circuit breaker behaviour: opens after the threshold, fast-fails while open, and
closes again after a successful half-open trial."""

from __future__ import annotations

import pytest
from app.core.circuit import CircuitBreaker
from app.core.errors import ProviderUnavailableError


async def _boom() -> None:
    raise RuntimeError("upstream down")


async def _ok() -> str:
    return "ok"


async def test_opens_after_threshold_and_fast_fails():
    breaker = CircuitBreaker("test", failure_threshold=3, reset_seconds=60)
    for _ in range(3):
        with pytest.raises(RuntimeError):
            await breaker.call(_boom)
    assert breaker.is_open
    # While open the breaker fast-fails with a typed error, without calling the function.
    with pytest.raises(ProviderUnavailableError):
        await breaker.call(_ok)


async def test_half_open_recovers_on_success():
    breaker = CircuitBreaker("test", failure_threshold=2, reset_seconds=0)
    for _ in range(2):
        with pytest.raises(RuntimeError):
            await breaker.call(_boom)
    # reset_seconds=0 means the cooldown is immediately over, so a trial is allowed.
    assert await breaker.call(_ok) == "ok"
    assert not breaker.is_open
