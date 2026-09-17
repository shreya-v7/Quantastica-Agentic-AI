"""Gemini Developer API client. Used on PLATFORM=local when GEMINI_API_KEY is set.

Vertex remains the GCP path (ADC / Workload Identity). This client is for rate-limited
Google AI Studio keys during local development. Never log the key.
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.errors import LLMError
from app.infra.llm.base import LLMClient, build_json_instruction, parse_json_response

logger = logging.getLogger("quantastica.llm")


class GeminiClient(LLMClient):
    def __init__(self, api_key: str, model: str, max_tokens: int):
        try:
            from google import genai
        except ImportError as exc:
            raise LLMError("google-genai is not installed") from exc
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens

    async def complete(
        self, system: str, user: str, json_schema: dict[str, Any] | None = None
    ) -> str | dict[str, Any]:
        if json_schema is not None:
            system = f"{system}\n\n{build_json_instruction(json_schema)}"
        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.0 if json_schema is not None else 0.3,
                max_output_tokens=self._max_tokens,
            )
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=user,
                config=config,
            )
        except Exception as exc:
            raise LLMError(f"Gemini API call failed: {exc}") from exc

        usage = getattr(response, "usage_metadata", None)
        logger.info(
            "llm.usage model=%s input_tokens=%s output_tokens=%s",
            self._model,
            getattr(usage, "prompt_token_count", None),
            getattr(usage, "candidates_token_count", None),
        )
        text = (response.text or "").strip()
        if not text:
            raise LLMError("Gemini returned an empty response")
        if json_schema is not None:
            return parse_json_response(text)
        return text
