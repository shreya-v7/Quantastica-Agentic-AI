"""Deterministic extractors. VLM is mocked in CI. casparser is optional."""

from __future__ import annotations

import json
import re
from typing import Any

from app.core.errors import ValidationError
from app.ingest.schemas import (
    AISExtract,
    CASExtract,
    CASLot,
    Form16Extract,
    TextEventExtract,
    assert_no_advice,
)

LAKH = 100_000
CRORE = 10_000_000

# Fixture Form 16 used when the VLM is mocked.
FORM16_FIXTURE = {
    "kind": "form16",
    "employer": "Northstar Labs Pvt Ltd",
    "pan_masked": "ABCDE****F",
    "basic_salary": {
        "amount": 3_600_000,
        "source_quote": "Basic Salary 3600000",
        "page": 1,
    },
    "confidence": 0.92,
}


def parse_form16(payload: dict[str, Any]) -> Form16Extract:
    assert_no_advice(payload)
    return Form16Extract.model_validate(payload)


def parse_ais(payload: dict[str, Any]) -> AISExtract:
    assert_no_advice(payload)
    return AISExtract.model_validate(payload)


def parse_cas(payload: dict[str, Any] | str) -> CASExtract:
    if isinstance(payload, str):
        try:
            import casparser  # type: ignore

            data = casparser.read_cas_pdf(payload)
            payload = data.model_dump() if hasattr(data, "model_dump") else dict(data)
        except Exception as exc:
            raise ValidationError(f"CAS parse failed: {exc}") from exc
    assert_no_advice(payload if isinstance(payload, dict) else {"raw": str(payload)})
    if "lots" in payload:
        return CASExtract.model_validate(payload)
    lots = []
    for folio in payload.get("folios", []):
        for scheme in folio.get("schemes", []):
            lots.append(
                CASLot(
                    symbol=scheme.get("isin") or scheme.get("symbol") or "UNKNOWN",
                    name=scheme.get("scheme") or scheme.get("name") or "Unknown",
                    quantity=float(scheme.get("close", scheme.get("quantity", 0))),
                    cost=float(scheme.get("cost", 0)),
                    acquired_on=str(scheme.get("acquired_on") or "2024-01-01"),
                    source_quote=str(scheme.get("scheme") or "CAS line"),
                )
            )
    return CASExtract(lots=lots, confidence=0.8)


_BONUS = re.compile(
    r"(?P<num>[\d,.]+)\s*(?P<unit>lakh|lac|crore|cr|rs)?\s*(?:bonus|income|salary)",
    re.I,
)
_DATE = re.compile(
    r"(\d{1,2})\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
    r"[a-z]*\s*(\d{4})?",
    re.I,
)
_MONTH = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _to_inr(num: str, unit: str | None) -> float:
    value = float(num.replace(",", ""))
    token = (unit or "").lower()
    if token in {"lakh", "lac"}:
        return value * LAKH
    if token in {"crore", "cr"}:
        return value * CRORE
    return value


def parse_text_event(raw: str) -> TextEventExtract:
    assert_no_advice({"raw": raw})
    bonus = _BONUS.search(raw)
    date_m = _DATE.search(raw)
    date = None
    if date_m:
        day = int(date_m.group(1))
        month = _MONTH[date_m.group(2)[:3].lower()]
        year = int(date_m.group(3) or 2026)
        date = f"{year:04d}-{month:02d}-{day:02d}"
    amount = None
    event_type = "note"
    if bonus:
        amount = _to_inr(bonus.group("num"), bonus.group("unit"))
        event_type = "bonus"
    return TextEventExtract(
        event_type=event_type,
        amount_inr=amount,
        date=date,
        raw=raw,
        confidence=0.9 if amount is not None else 0.4,
    )


class MockVLM:
    """Returns the Form 16 fixture. Rejects injected advice in tests via parse_form16."""

    def extract(self, kind: str, image_b64: str | None, override: dict | None = None) -> dict:
        if override is not None:
            return override
        if kind == "form16":
            return json.loads(json.dumps(FORM16_FIXTURE))
        if kind == "ais":
            return {
                "kind": "ais",
                "interest_inr": {"amount": 12_000, "source_quote": "Interest 12000", "page": 1},
                "dividend_inr": {"amount": 0, "source_quote": "Dividend 0", "page": 1},
                "confidence": 0.8,
            }
        if kind == "cas":
            return {
                "kind": "cas",
                "lots": [
                    {
                        "symbol": "INFY.NS",
                        "name": "Infosys",
                        "quantity": 10,
                        "cost": 1500,
                        "acquired_on": "2025-01-15",
                        "source_quote": "INFY 10 units @ 1500",
                    }
                ],
                "confidence": 0.88,
            }
        raise ValidationError(f"No mock VLM fixture for kind={kind}")
