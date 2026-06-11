"""Response envelope helpers. Every /api/* response uses this shape."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app import __version__
from app.core.context import get_request_id


def meta() -> dict[str, str]:
    return {"requestId": get_request_id(), "version": __version__}


def _dump(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(by_alias=True)
    if isinstance(value, list):
        return [_dump(item) for item in value]
    return value


def success(data: Any) -> dict[str, Any]:
    return {"ok": True, "data": _dump(data), "error": None, "meta": meta()}


def failure(code: str, message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "data": None,
        "error": {"code": code, "message": message},
        "meta": meta(),
    }
