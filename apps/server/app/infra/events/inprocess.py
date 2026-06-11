"""In-process event publisher for tests and zero-dependency dev.

Events are logged and kept in a bounded ring buffer that tests can inspect. This is a
real publisher with observable delivery, not a no-op.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Any

from app.infra.events.base import EventPublisher

logger = logging.getLogger("quantastica.events")


class InProcessEventPublisher(EventPublisher):
    def __init__(self, max_events: int = 1000):
        self.events: deque[dict[str, Any]] = deque(maxlen=max_events)

    async def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        event = {"type": event_type, "payload": payload}
        self.events.append(event)
        logger.info("event %s %s", event_type, payload)
