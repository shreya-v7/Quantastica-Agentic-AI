import json
from typing import Any


_STORE: dict[str, Any] = {}
_QUEUE: list[dict[str, Any]] = []


async def queue(topic: str, payload: Any) -> None:
    _QUEUE.append({"topic": topic, "payload": payload})


async def store(key: str, value: Any) -> None:
    _STORE[key] = value


async def fetch(key: str) -> Any:
    return _STORE.get(key)


async def run(job: str, payload: Any) -> Any:
    return {"provider": "gcp", "job": job, "status": "accepted", "payload": payload}


async def ai(prompt: str, context: Any | None = None) -> str:
    context_blob = json.dumps(context, ensure_ascii=True)[:1500] if context else "{}"
    return (
        "GCP AI response: "
        f"{prompt}. Context summary length={len(context_blob)} characters."
    )
