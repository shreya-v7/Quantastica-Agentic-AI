"""LangGraph ingest: route by kind, parse, validate, interrupt on low confidence."""

from __future__ import annotations

from typing import Literal, TypedDict

from langgraph.graph import END, StateGraph

from app.core.errors import ValidationError
from app.ingest.extractors import (
    MockVLM,
    parse_ais,
    parse_cas,
    parse_form16,
    parse_text_event,
)

CONFIDENCE_FLOOR = 0.7


class IngestState(TypedDict, total=False):
    household_id: str
    kind: str
    raw_text: str
    image_b64: str | None
    vlm_override: dict | None
    extracted: dict
    confidence: float
    needs_review: bool
    missing_fields: list[str]
    error: str | None


def route_kind(state: IngestState) -> Literal["text", "form16", "ais", "cas", "reject"]:
    kind = state.get("kind") or "text_event"
    if kind in {"text", "text_event", "audio"}:
        return "text"
    if kind in {"form16", "ais", "cas", "image"}:
        return "form16" if kind == "image" else kind  # type: ignore[return-value]
    return "reject"


def parse_text(state: IngestState) -> IngestState:
    extracted = parse_text_event(state.get("raw_text") or "")
    return {
        **state,
        "extracted": extracted.model_dump(mode="json"),
        "confidence": extracted.confidence,
        "needs_review": extracted.confidence < CONFIDENCE_FLOOR
        or extracted.amount_inr is None,
        "missing_fields": [] if extracted.amount_inr is not None else ["amount_inr"],
    }


def parse_vision(state: IngestState) -> IngestState:
    kind = state.get("kind") or "form16"
    if kind == "image":
        kind = "form16"
    raw = MockVLM().extract(kind, state.get("image_b64"), state.get("vlm_override"))
    if kind == "form16":
        extracted = parse_form16(raw)
        payload = extracted.model_dump(mode="json")
        missing = [] if extracted.basic_salary.amount else ["basic_salary"]
        conf = extracted.confidence
    elif kind == "ais":
        extracted_ais = parse_ais(raw)
        payload = extracted_ais.model_dump(mode="json")
        missing = []
        conf = extracted_ais.confidence
    else:
        extracted_cas = parse_cas(raw)
        payload = extracted_cas.model_dump(mode="json")
        missing = []
        conf = extracted_cas.confidence
    return {
        **state,
        "extracted": payload,
        "confidence": conf,
        "needs_review": conf < CONFIDENCE_FLOOR or bool(missing),
        "missing_fields": missing,
    }


def reject(state: IngestState) -> IngestState:
    return {**state, "error": f"Unsupported ingest kind {state.get('kind')}", "needs_review": True}


def build_ingest_graph():
    graph = StateGraph(IngestState)
    graph.add_node("text", parse_text)
    graph.add_node("form16", parse_vision)
    graph.add_node("ais", parse_vision)
    graph.add_node("cas", parse_vision)
    graph.add_node("reject", reject)
    graph.set_conditional_entry_point(
        route_kind,
        {"text": "text", "form16": "form16", "ais": "ais", "cas": "cas", "reject": "reject"},
    )
    graph.add_edge("text", END)
    graph.add_edge("form16", END)
    graph.add_edge("ais", END)
    graph.add_edge("cas", END)
    graph.add_edge("reject", END)
    return graph.compile()


INGEST_GRAPH = build_ingest_graph()


def run_ingest(state: IngestState) -> IngestState:
    result = INGEST_GRAPH.invoke(state)
    if result.get("error"):
        raise ValidationError(str(result["error"]))
    return result
