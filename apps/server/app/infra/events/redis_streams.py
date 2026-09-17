"""Redis Streams event publisher. The worker consumes the same stream."""

from __future__ import annotations

import json
import logging
from typing import Any

from redis.asyncio import Redis

from app.infra.events.base import EventPublisher

logger = logging.getLogger("quantastica.events")

STREAM_KEY = "quantastica:events"
MAX_STREAM_LEN = 100_000


class RedisStreamsPublisher(EventPublisher):
    def __init__(self, redis: Redis):
        self._redis = redis

    async def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        await self._redis.xadd(
            STREAM_KEY,
            {"type": event_type, "payload": json.dumps(payload)},
            maxlen=MAX_STREAM_LEN,
            approximate=True,
        )
        logger.info("event %s %s", event_type, payload)
