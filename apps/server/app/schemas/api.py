from typing import Generic, TypeVar

from pydantic import BaseModel

from app.schemas.base import Contract

T = TypeVar("T")


class ApiError(Contract):
    code: str
    message: str


class ApiMeta(Contract):
    request_id: str
    version: str


class ApiEnvelope(BaseModel, Generic[T]):
    ok: bool
    data: T | None = None
    error: ApiError | None = None
    meta: ApiMeta
