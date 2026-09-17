"""Vertex AI LLM client for the gcp platform.

Uses Anthropic's Claude models served through Vertex AI. Credentials come from
Application Default Credentials or Workload Identity, never a key file in the repo.
"""

from __future__ import annotations

import logging
from typing import Any

from anthropic import AnthropicError, AsyncAnthropicVertex

from app.core.errors import LLMError
from app.infra.llm.base import LLMClient, build_json_instruction, parse_json_response

logger = logging.getLogger("quantastica.llm")


class VertexClient(LLMClient):
    def __init__(self, project: str, region: str, model: str, max_tokens: int):
        self._client = AsyncAnthropicVertex(project_id=project, region=region)
        self._model = model
        self._max_tokens = max_tokens

    async def complete(
        self, system: str, user: str, json_schema: dict[str, Any] | None = None
    ) -> str | dict[str, Any]:
        if json_schema is not None:
            system = f"{system}\n\n{build_json_instruction(json_schema)}"
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                temperature=0.0 if json_schema is not None else 0.3,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
        except AnthropicError as exc:
            raise LLMError(f"Vertex AI call failed: {exc}") from exc

        usage = response.usage
        logger.info(
            "vertex complete model=%s input_tokens=%s output_tokens=%s",
            self._model,
            usage.input_tokens,
            usage.output_tokens,
        )
        text = "".join(block.text for block in response.content if block.type == "text")
        return parse_json_response(text) if json_schema is not None else text
