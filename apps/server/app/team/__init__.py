"""ADK-shaped team. Google ADK is the cloud host; this runtime is the portable graph.

Sub-agent depth is at most 2. The kernel is not an agent. Existing LangGraph ingest
is wrapped as a tool.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from quantastica_kernel.guard import fail_closed, screen
from quantastica_kernel.reconcile import decide
from quantastica_kernel.verify import verify_money_fields

from app.ingest.graph import run_ingest
from app.trading.intents import parse_order_text, pretrade_notes

State = dict[str, Any]
Tool = Callable[[State], State]


@dataclass
class Node:
    name: str
    run: Tool


class SequentialAgent:
    def __init__(self, name: str, children: list[Node]):
        self.name = name
        self.children = children

    def run(self, state: State) -> State:
        for child in self.children:
            state = child.run(state)
            state.setdefault("trace", []).append(child.name)
        return state


class ParallelAgent:
    def __init__(self, name: str, children: list[Node]):
        self.name = name
        self.children = children

    def run(self, state: State) -> State:
        merged = dict(state)
        extracts = {}
        for child in self.children:
            try:
                piece = child.run(dict(state))
                extracts[child.name] = piece.get("extracted") or piece
            except Exception as exc:
                extracts[child.name] = {"error": str(exc), "needs_review": True}
            merged.setdefault("trace", []).append(child.name)
        merged["extracted_group"] = extracts
        if state.get("kind") and state["kind"] in extracts:
            merged["extracted"] = extracts.get(state["kind"]) or merged.get("extracted")
        return merged


class LoopAgent:
    def __init__(self, name: str, child: Node, max_retries: int = 2):
        self.name = name
        self.child = child
        self.max_retries = max_retries

    def run(self, state: State) -> State:
        attempt = 0
        current = dict(state)
        while True:
            current = self.child.run(current)
            current.setdefault("trace", []).append(self.child.name)
            report = verify_money_fields(current.get("extracted") or {}, attempt)
            current["verify"] = report
            if report["ok"]:
                return current
            if report["retry"]:
                attempt += 1
                continue
            current["needs_review"] = True
            return current


def _classify(state: State) -> State:
    kind = state.get("kind") or "text_event"
    return {**state, "kind": kind}


def _form16(state: State) -> State:
    return {**state, "kind": "form16", **run_ingest({**state, "kind": "form16"})}


def _ais(state: State) -> State:
    return {**state, "kind": "ais", **run_ingest({**state, "kind": "ais"})}


def _cas(state: State) -> State:
    return {**state, "kind": "cas", **run_ingest({**state, "kind": "cas"})}


def _bank(state: State) -> State:
    return {
        **state,
        "extracted": {"kind": "bank_statement", "confidence": 0.5},
        "needs_review": True,
    }


def _contract_note(state: State) -> State:
    return {
        **state,
        "extracted": {"kind": "contract_note", "confidence": 0.5},
        "needs_review": True,
    }


def _verify(state: State) -> State:
    report = verify_money_fields(
        state.get("extracted") or {}, int(state.get("verify_attempts") or 0)
    )
    return {
        **state,
        "verify": report,
        "needs_review": report["needs_review"] or state.get("needs_review"),
    }


def _reconcile(state: State) -> State:
    left = state.get("name_a") or ""
    right = state.get("name_b") or ""
    decision = decide(left, right, state.get("folio_a") or "", state.get("folio_b") or "")
    return {**state, "match": decision.__dict__}


def _explain(state: State) -> State:
    return {**state, "explained": True}


def _trading(state: State) -> State:
    enabled = bool(state.get("trading_chat_enabled"))
    text = str(state.get("query") or "")
    if not enabled:
        return {**state, "trade": {"blocked": True, "reason": "TRADING_CHAT_ENABLED is false"}}
    draft = parse_order_text(text)
    notes = pretrade_notes(draft.symbol, draft.side, None)
    return {**state, "trade": {
        "draft": draft.model_dump(mode="json"), "notes": notes, "paper": True,
    }}


def _guard(state: State) -> State:
    answer = str(state.get("answer") or "")
    allowed = list(state.get("allowed_amounts") or [])
    quotes = list(state.get("source_quotes") or [])
    blocked = fail_closed(answer, allowed, quotes)
    verdict = screen(answer, allowed, quotes)
    return {**state, "answer": blocked, "guard": verdict.__dict__}


@dataclass
class QuantasticaTeam:
    """Orchestrator plus depth-2 sub-agents. Verifier is a sibling of extractors."""

    trace: list[str] = field(default_factory=list)

    def ingest_coordinator(self) -> SequentialAgent:
        extractors = ParallelAgent("extraction_team", [
            Node("form16", _form16),
            Node("ais", _ais),
            Node("cas", _cas),
            Node("contract_note", _contract_note),
            Node("bank_statement", _bank),
        ])
        verify_loop = LoopAgent("verify_loop", Node("verify", _verify), max_retries=2)
        return SequentialAgent("ingest_coordinator", [
            Node("doc_classifier", _classify),
            Node("extraction_team", extractors.run),
            Node("verify_loop", verify_loop.run),
        ])

    def run(self, state: State) -> State:
        route = state.get("route") or "ingest"
        current = {**state, "trace": list(state.get("trace") or [])}
        current.setdefault("trace", []).append("orchestrator")
        if route == "ingest":
            current = self.ingest_coordinator().run(current)
        elif route == "reconcile":
            current = Node("reconciler", _reconcile).run(current)
            current.setdefault("trace", []).append("reconciler")
        elif route == "explain":
            current = Node("explainer", _explain).run(current)
            current.setdefault("trace", []).append("explainer")
        elif route == "trade":
            current = Node("trading_assistant", _trading).run(current)
            current.setdefault("trace", []).append("trading_assistant")
        current = Node("guard", _guard).run(current)
        current.setdefault("trace", []).append("guard")
        self.trace = list(current.get("trace") or [])
        return current
