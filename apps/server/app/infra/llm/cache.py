"""Deterministic LLM response cache (Phase K).

Temperature-0 calls (those carrying a JSON schema) are pure functions of
system + user + schema, so they are cached in Redis for 24h keyed by a content hash.
Free-form calls (no schema, temperature > 0) are never cached. A per-request contextvar
lets dev bypass the cache via the `X-LLM-Cache-Bypass` header.
"""

from __future__ import annotations

import contextvars
import hashlib
import json
import logging
from typing import Any

from app.infra.llm.base import LLMClient

logger = logging.getLogger("quantastica.llm")

cache_bypass: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "llm_cache_bypass", default=False
)

_TTL_SECONDS = 24 * 3600


def _key(system: str, user: str, json_schema: dict[str, Any]) -> str:
    blob = json.dumps(
        {"system": system, "user": user, "schema": json_schema}, sort_keys=True
    )
    return "llm:resp:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


class CachingLLM(LLMClient):
    def __init__(self, inner: LLMClient, cache, ttl_seconds: int = _TTL_SECONDS):
        self._inner = inner
        self._cache = cache
        self._ttl = ttl_seconds

    async def complete(
        self, system: str, user: str, json_schema: dict[str, Any] | None = None
    ) -> str | dict[str, Any]:
        if json_schema is None or cache_bypass.get():
            return await self._inner.complete(system, user, json_schema)

        key = _key(system, user, json_schema)
        try:
            cached = await self._cache.get(key)
        except Exception as exc:  # cache is best-effort; never block the call path
            logger.warning("llm cache get failed: %s", exc)
            cached = None
        if cached is not None:
            logger.info("llm cache hit")
            return json.loads(cached)

        result = await self._inner.complete(system, user, json_schema)
        try:
            await self._cache.set(key, json.dumps(result), ex=self._ttl)
        except Exception as exc:
            logger.warning("llm cache set failed: %s", exc)
        return result
