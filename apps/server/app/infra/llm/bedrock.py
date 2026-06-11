"""Bedrock LLM client for the aws platform.

Invokes an Anthropic Claude model on Bedrock. Credentials come from the task or
execution role, never static keys in prod.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.errors import LLMError
from app.infra.llm.base import LLMClient, build_json_instruction, parse_json_response

logger = logging.getLogger("quantastica.llm")


class BedrockClient(LLMClient):
    def __init__(self, region: str, model_id: str, max_tokens: int):
        self._client = boto3.client("bedrock-runtime", region_name=region)
        self._model_id = model_id
        self._max_tokens = max_tokens

    async def complete(
        self, system: str, user: str, json_schema: dict[str, Any] | None = None
    ) -> str | dict[str, Any]:
        if json_schema is not None:
            system = f"{system}\n\n{build_json_instruction(json_schema)}"
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self._max_tokens,
            "temperature": 0.0 if json_schema is not None else 0.3,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        try:
            response = await asyncio.to_thread(
                self._client.invoke_model,
                modelId=self._model_id,
                body=json.dumps(body),
            )
        except (BotoCoreError, ClientError) as exc:
            raise LLMError(f"Bedrock call failed: {exc}") from exc

        payload = json.loads(response["body"].read())
        usage = payload.get("usage", {})
        logger.info(
            "bedrock complete model=%s input_tokens=%s output_tokens=%s",
            self._model_id,
            usage.get("input_tokens"),
            usage.get("output_tokens"),
        )
        text = "".join(
            block.get("text", "")
            for block in payload.get("content", [])
            if block.get("type") == "text"
        )
        return parse_json_response(text) if json_schema is not None else text
