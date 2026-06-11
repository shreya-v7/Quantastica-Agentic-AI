"""Insight agent: one LLM call producing validated findings tied to metric ids."""

from __future__ import annotations

from pydantic import Field

from app.agents import prompts
from app.agents.base import PipelineContext
from app.agents.llm_json import complete_json
from app.core.ids import new_id, now_iso
from app.schemas.agents import Finding
from app.schemas.base import Contract
from app.schemas.common import Severity


class InsightDraft(Contract):
    title: str
    body: str
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    metric_ids: list[str]


class InsightDraftList(Contract):
    findings: list[InsightDraft] = Field(min_length=1)


class InsightAgent:
    name = "insight"

    def __init__(self, retries: int):
        self._retries = retries

    def input_summary(self, ctx: PipelineContext) -> str:
        return f"{len(ctx.risk_metrics)} risk metrics"

    async def run(self, ctx: PipelineContext) -> str:
        if ctx.metrics is None:
            raise ValueError("Insight agent requires researcher metrics")
        valid_ids = {m.id for m in ctx.risk_metrics}
        user = prompts.insight_user(ctx.query, ctx.metrics, ctx.risk_metrics)
        drafts = await complete_json(
            ctx.llm, prompts.INSIGHT_SYSTEM, user, InsightDraftList, self._retries
        )
        findings: list[Finding] = []
        for draft in drafts.findings:
            cited = [mid for mid in draft.metric_ids if mid in valid_ids]
            findings.append(
                Finding(
                    id=new_id("fnd"),
                    portfolio_id=ctx.portfolio.id,
                    run_id=ctx.run_id,
                    title=draft.title,
                    body=draft.body,
                    severity=draft.severity,
                    confidence=draft.confidence,
                    metric_ids=cited,
                    created_at=now_iso(),
                )
            )
        ctx.findings = findings
        return f"{len(findings)} findings produced"
