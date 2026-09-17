"""Phase 2 ingest: mocked VLM, advice reject, interrupt on missing fields."""

from __future__ import annotations

import pytest
from app.core.errors import ValidationError
from app.ingest.extractors import FORM16_FIXTURE, parse_form16, parse_text_event
from app.ingest.graph import run_ingest
from app.ingest.schemas import assert_no_advice


def test_form16_fixture_parses():
    extracted = parse_form16(FORM16_FIXTURE)
    assert extracted.basic_salary.amount == 3_600_000
    assert extracted.basic_salary.source_quote
    assert "tax" not in extracted.model_dump()


def test_vlm_tax_due_is_rejected():
    payload = {
        **FORM16_FIXTURE,
        "basic_salary": {
            "amount": 1,
            "source_quote": "tax due 50000",
            "page": 1,
        },
    }
    with pytest.raises(ValidationError, match="tax-due or advisory"):
        parse_form16(payload)


def test_switch_regime_in_payload_is_rejected():
    with pytest.raises(ValidationError):
        assert_no_advice({"advice": "switch regime now"})


def test_injected_advice_in_graph_override_is_rejected():
    with pytest.raises(ValidationError):
        run_ingest(
            {
                "kind": "form16",
                "vlm_override": {
                    **FORM16_FIXTURE,
                    "basic_salary": {
                        "amount": 100,
                        "source_quote": "you should sell RELIANCE",
                        "page": 1,
                    },
                },
            }
        )


def test_missing_amount_triggers_review():
    state = run_ingest({"kind": "text_event", "raw_text": "note without a rupee"})
    assert state["needs_review"] is True
    assert "amount_inr" in state["missing_fields"]
    assert state["extracted"]["amount_inr"] is None


def test_lakh_bonus_parses_to_inr():
    event = parse_text_event("Add a 12 lakh bonus on 12 Sep 2026")
    assert event.event_type == "bonus"
    assert event.amount_inr == 1_200_000
    assert event.date == "2026-09-12"
    assert event.confidence >= 0.7


def test_form16_graph_high_confidence():
    state = run_ingest({"kind": "form16"})
    assert state["needs_review"] is False
    assert state["extracted"]["basic_salary"]["amount"] == 3_600_000


def test_cas_fixture_lots():
    state = run_ingest({"kind": "cas"})
    assert state["needs_review"] is False
    assert state["extracted"]["lots"][0]["symbol"] == "INFY.NS"
