from typing import Any

from app.financial_intelligence.cloud.index import cloud


async def emit(topic: str, payload: Any) -> None:
    await cloud.queue(topic, payload)
