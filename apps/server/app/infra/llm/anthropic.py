"""Anthropic API LLM client for the local platform."""

from __future__ import annotations

import logging
from typing import Any

from anthropic import APIError, AsyncAnthropic

from app.core.errors import LLMError
from app.infra.llm.base import LLMClient, build_json_instruction, parse_json_response

logger = logging.getLogger("quantastica.llm")

# Approximate USD per 1M tokens (input, output) for cost telemetry (Phase M). Falls back
# to a sensible default when the configured model is not in the table.
_PRICING: dict[str, tuple[float, float]] = {
    "claude-3-5-haiku": (0.80, 4.0),
    "claude-3-5-sonnet": (3.0, 15.0),
    "claude-3-7-sonnet": (3.0, 15.0),
}


def _estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    in_rate, out_rate = next(
        (rates for prefix, rates in _PRICING.items() if model.startswith(prefix)),
        (3.0, 15.0),
    )
    return round((input_tokens * in_rate + output_tokens * out_rate) / 1_000_000, 6)


class AnthropicClient(LLMClient):
    def __init__(self, api_key: str, model: str, max_tokens: int):
        # Hard 60s ceiling on the slowest outbound dependency (Phase K).
        self._client = AsyncAnthropic(api_key=api_key, timeout=60.0)
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
            "llm.usage model=%s input_tokens=%s output_tokens=%s cost_usd=%s",
            self._model,
            usage.input_tokens,
            usage.output_tokens,
            _estimate_cost_usd(self._model, usage.input_tokens, usage.output_tokens),
        )

        text = "".join(block.text for block in response.content if block.type == "text")
        if json_schema is not None:
            return parse_json_response(text)
        return text
