"""Anthropic API LLM client for the local platform."""

from __future__ import annotations

import logging
from typing import Any

from anthropic import APIError, AsyncAnthropic

from app.core.errors import LLMError
from app.infra.llm.base import LLMClient, build_json_instruction, parse_json_response

logger = logging.getLogger("quantastica.llm")


class AnthropicClient(LLMClient):
    def __init__(self, api_key: str, model: str, max_tokens: int):
        self._client = AsyncAnthropic(api_key=api_key)
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
        except APIError as exc:
            raise LLMError(f"Anthropic API call failed: {exc}") from exc

        usage = response.usage
        logger.info(
            "anthropic complete model=%s input_tokens=%s output_tokens=%s",
            self._model,
            usage.input_tokens,
            usage.output_tokens,
        )

        text = "".join(block.text for block in response.content if block.type == "text")
        if json_schema is not None:
            return parse_json_response(text)
        return text
