"""LLM client interface.

Three real implementations: Anthropic API (local), Vertex AI (gcp), Bedrock (aws).
`complete` returns a str for prose and a parsed dict when a json_schema is supplied.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from typing import Any

from app.core.errors import LLMError

_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


class LLMClient(ABC):
    @abstractmethod
    async def complete(
        self, system: str, user: str, json_schema: dict[str, Any] | None = None
    ) -> str | dict[str, Any]: ...


def build_json_instruction(json_schema: dict[str, Any]) -> str:
    return (
        "Respond with a single valid JSON object only, with no prose and no code fences. "
        f"It must conform to this JSON schema:\n{json.dumps(json_schema)}"
    )


def parse_json_response(text: str) -> dict[str, Any]:
    cleaned = _FENCE.sub("", text.strip())
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise LLMError(f"Model did not return valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise LLMError("Model returned JSON that is not an object")
    return parsed
