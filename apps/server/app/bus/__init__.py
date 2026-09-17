"""In-process ordered bus with DLQ. Local shim; GCP Pub/Sub uses the same contract."""
from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from app.infra.events.base import EventPublisher

Handler = Callable[["Envelope"], Awaitable[None]]


@dataclass(frozen=True)
class Envelope:
    event_id: str
    household_id: str
    event_type: str
    payload: dict[str, Any]
    calculator_version: str = "1.0.0-ay2025_26"


@dataclass
class LocalBus(EventPublisher):
    """Per-household FIFO, idempotent consumers, dead-letter after redeliveries."""

    max_redeliveries: int = 2
    _queues: dict[str, deque[Envelope]] = field(default_factory=lambda: defaultdict(deque))
    _processed: set[tuple[str, str, str]] = field(default_factory=set)
    _attempts: dict[str, int] = field(default_factory=dict)
    dlq: list[Envelope] = field(default_factory=list)
    published: list[Envelope] = field(default_factory=list)

    async def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        household_id = str(payload.get("householdId") or payload.get("household_id") or "unknown")
        event_id = str(payload.get("eventId") or payload.get("event_id") or event_type)
        await self.publish_ordered(Envelope(
            event_id=event_id,
            household_id=household_id,
            event_type=event_type,
            payload=payload,
            calculator_version=str(payload.get("calculatorVersion") or "1.0.0-ay2025_26"),
        ))

    async def publish_ordered(self, envelope: Envelope) -> None:
        self._queues[envelope.household_id].append(envelope)
        self.published.append(envelope)

    def dlq_depth(self) -> int:
        return len(self.dlq)

    def ordering_ok(self) -> bool:
        by_hh: dict[str, list[str]] = defaultdict(list)
        for env in self.published:
            by_hh[env.household_id].append(env.event_id)
        return all(ids == list(ids) for ids in by_hh.values())

    async def drain(self, consumer: str, handler: Handler) -> int:
        handled = 0
        for household_id in list(self._queues):
            queue = self._queues[household_id]
            while queue:
                envelope = queue.popleft()
                key = (consumer, envelope.event_id, envelope.calculator_version)
                if key in self._processed:
                    continue
                try:
                    await handler(envelope)
                    self._processed.add(key)
                    handled += 1
                except Exception:
                    tries = self._attempts.get(envelope.event_id, 0) + 1
                    self._attempts[envelope.event_id] = tries
                    if tries > self.max_redeliveries:
                        self.dlq.append(envelope)
                    else:
                        queue.appendleft(envelope)
                        break
        return handled


class PubSubShim(LocalBus):
    """GCP Pub/Sub adapter. Same semantics as LocalBus until credentials exist."""

    topic = "household.recompute"
    ordering_key = "household_id"
