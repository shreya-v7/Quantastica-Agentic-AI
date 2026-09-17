"""LangGraph state for the grounded analysis pipeline.

The graph carries only a failure flag. Portfolio math, findings, and the AgentRun live
on PipelineContext and are persisted by the orchestrator after every node. That keeps
LangGraph as control flow without making the money path depend on checkpointing.
"""

from __future__ import annotations

from typing import TypedDict


class GraphState(TypedDict, total=False):
    failed: bool
    last_step: str
