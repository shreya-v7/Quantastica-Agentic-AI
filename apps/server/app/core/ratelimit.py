"""Redis fixed-window rate limiter. Fails open if Redis is unreachable so a cache
outage never locks every user out, but logs so the gap is visible."""

from __future__ import annotations

import logging

from redis.asyncio import Redis

from app.core.errors import RateLimitedError

logger = logging.getLogger("quantastica.ratelimit")


class RateLimiter:
    def __init__(self, redis: Redis):
        self._redis = redis

    async def hit(self, key: str, limit: int, window_seconds: int) -> None:
        bucket = f"rl:{key}"
        try:
            count = await self._redis.incr(bucket)
            if count == 1:
                await self._redis.expire(bucket, window_seconds)
        except Exception as exc:
            logger.warning("rate limiter degraded for %s: %s", key, exc)
            return
        if count > limit:
            ttl = await self._redis.ttl(bucket)
            raise RateLimitedError(
                "Too many requests. Slow down and retry shortly.",
                retry_after_seconds=max(1, int(ttl)),
            )
