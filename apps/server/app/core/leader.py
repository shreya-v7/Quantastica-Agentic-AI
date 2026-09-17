"""Single-leader lock over Redis so exactly one worker evaluates rules at a time.

The lock is a SET NX with a TTL, renewed each tick. If the holder dies the TTL lets
another instance take over. Acquisition and renewal are best-effort and never raise.
"""

from __future__ import annotations

import contextlib
import logging
import uuid

from redis.asyncio import Redis

logger = logging.getLogger("quantastica.leader")

_RELEASE = """
if redis.call('get', KEYS[1]) == ARGV[1] then
  return redis.call('del', KEYS[1])
else
  return 0
end
"""


class LeaderLock:
    def __init__(self, redis: Redis, key: str, ttl_seconds: int):
        self._redis = redis
        self._key = key
        self._ttl = ttl_seconds
        self._token = uuid.uuid4().hex
        self.is_leader = False

    async def acquire_or_renew(self) -> bool:
        try:
            if self.is_leader:
                # Renew only if we still own it.
                ok = await self._redis.set(
                    self._key, self._token, xx=True, ex=self._ttl
                )
                self.is_leader = bool(ok)
            else:
                ok = await self._redis.set(
                    self._key, self._token, nx=True, ex=self._ttl
                )
                self.is_leader = bool(ok)
        except Exception as exc:
            logger.warning("leader lock unavailable: %s", exc)
            self.is_leader = False
        return self.is_leader

    async def release(self) -> None:
        with contextlib.suppress(Exception):
            await self._redis.eval(_RELEASE, 1, self._key, self._token)
