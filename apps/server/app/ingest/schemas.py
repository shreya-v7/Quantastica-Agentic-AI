"""Pydantic extractors. No tax-due or advice fields. Amounts carry a source quote."""

from __future__ import annotations

import re

from pydantic import Field, field_validator

from app.core.errors import ValidationError
from app.schemas.base import Contract

ADVICE_RE = re.compile(
    r"tax due|switch regime|you should (buy|sell|switch)|invest in|not investment advice",
    re.I,
)


def reject_advice_text(*parts: str) -> None:
    blob = " ".join(p for p in parts if p)
    if ADVICE_RE.search(blob):
        raise ValidationError("Extractor output contained tax-due or advisory language.")


class MoneyField(Contract):
    amount: float = Field(ge=0)
    source_quote: str = Field(min_length=1)
    page: int = Field(default=1, ge=1)
    bbox: list[float] | None = None

    @field_validator("source_quote")
    @classmethod
    def _quote(cls, value: str) -> str:
        reject_advice_text(value)
        return value


class Form16Extract(Contract):
    kind: str = "form16"
    employer: str
    pan_masked: str
    basic_salary: MoneyField
    confidence: float = Field(ge=0, le=1)


class AISExtract(Contract):
    kind: str = "ais"
    interest_inr: MoneyField
    dividend_inr: MoneyField
    confidence: float = Field(ge=0, le=1)


class CASLot(Contract):
    symbol: str
    name: str
    quantity: float = Field(ge=0)
    cost: float = Field(ge=0)
    acquired_on: str
    source_quote: str


class CASExtract(Contract):
    kind: str = "cas"
    lots: list[CASLot]
    confidence: float = Field(ge=0, le=1)


class TextEventExtract(Contract):
    kind: str = "text_event"
    event_type: str
    amount_inr: float | None = None
    date: str | None = None
    symbol: str | None = None
    raw: str
    confidence: float = Field(ge=0, le=1)


def assert_no_advice(payload: dict) -> None:
    reject_advice_text(str(payload))
    if "taxDue" in payload or "tax_due" in payload or "advice" in payload:
        raise ValidationError("Extractor schema forbids tax-due or advice fields.")
