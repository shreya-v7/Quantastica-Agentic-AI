"""Model gateway: failover, per-tenant cost, gen_ai span events (not attributes)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.errors import LLMError, RateLimitedError
from app.infra.llm.base import LLMClient


@dataclass
class TokenMeter:
    by_tenant: dict[str, dict[str, float]] = field(default_factory=dict)
    failovers: int = 0
    spans: list[dict[str, Any]] = field(default_factory=list)

    def record(self, tenant: str, provider: str, model: str, in_tokens: int, out_tokens: int,
               latency_ms: float, cost_usd: float) -> None:
        bucket = self.by_tenant.setdefault(tenant, {"tokens": 0, "cost": 0.0, "calls": 0})
        bucket["tokens"] += in_tokens + out_tokens
        bucket["cost"] += cost_usd
        bucket["calls"] += 1
        self.spans.append({
            "name": "gen_ai.completion",
            "attributes": {
                "gen_ai.system": provider,
                "gen_ai.request.model": model,
                "gen_ai.usage.input_tokens": in_tokens,
                "gen_ai.usage.output_tokens": out_tokens,
                "gen_ai.operation.name": "chat",
            },
            "events": [{"name": "gen_ai.content", "redacted": True}],
            "latency_ms": latency_ms,
        })


class FailoverLLM(LLMClient):
    def __init__(self, primary: LLMClient, secondary: LLMClient | None, meter: TokenMeter,
                 tenant: str = "default", limit: int = 120):
        self._primary = primary
        self._secondary = secondary
        self._meter = meter
        self._tenant = tenant
        self._limit = limit
        self._hits = 0

    async def complete(
        self, system: str, user: str, json_schema: dict[str, Any] | None = None
    ) -> str | dict[str, Any]:
        self._hits += 1
        if self._hits > self._limit:
            raise RateLimitedError("Per-tenant model rate limit", retry_after_seconds=60)
        try:
            result = await self._primary.complete(system, user, json_schema)
            provider = type(self._primary).__name__
        except Exception as exc:
            if self._secondary is None:
                raise LLMError(str(exc)) from exc
            self._meter.failovers += 1
            result = await self._secondary.complete(system, user, json_schema)
            provider = type(self._secondary).__name__
        in_tokens = max(1, len(system.split()) + len(user.split()))
        out_tokens = max(1, len(str(result).split()))
        self._meter.record(self._tenant, provider, "gateway", in_tokens, out_tokens, 1.0,
                           (in_tokens + out_tokens) * 0.000002)
        return result
