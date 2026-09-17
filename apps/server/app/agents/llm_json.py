"""Validate-retry-fail helper for LLM JSON outputs.

Calls the model, validates the result against a Pydantic model, and on failure retries
once with the validation error included in the prompt, then raises LLMError.
"""

from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from app.core.errors import LLMError
from app.infra.llm.base import LLMClient

T = TypeVar("T", bound=BaseModel)


async def complete_json(
    llm: LLMClient,
    system: str,
    user: str,
    model: type[T],
    retries: int,
) -> T:
    schema = model.model_json_schema(by_alias=True)
    prompt = user
    last_error: Exception | None = None
    for _ in range(retries + 1):
        try:
            data = await llm.complete(system, prompt, json_schema=schema)
            return model.model_validate(data)
        except (LLMError, PydanticValidationError) as exc:
            last_error = exc
            prompt = (
                f"{user}\n\nYour previous response was invalid: {exc}. "
                "Return corrected JSON only."
            )
    raise LLMError(f"LLM produced invalid output after retries: {last_error}")
