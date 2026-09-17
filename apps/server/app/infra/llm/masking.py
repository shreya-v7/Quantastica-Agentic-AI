"""Mask PAN and account numbers on every LLM prompt (DPDP)."""

from __future__ import annotations

from typing import Any

from app.infra.llm.base import LLMClient
from app.privacy import mask_pii


class MaskingLLM(LLMClient):
    def __init__(self, inner: LLMClient):
        self._inner = inner

    async def complete(
        self, system: str, user: str, json_schema: dict[str, Any] | None = None
    ) -> str | dict[str, Any]:
        return await self._inner.complete(mask_pii(system), mask_pii(user), json_schema)
