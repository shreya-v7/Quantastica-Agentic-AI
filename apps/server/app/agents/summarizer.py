"""Summarizer agent: one LLM call producing the final plain-language answer."""

from __future__ import annotations

from app.agents import prompts
from app.agents.base import PipelineContext


class SummarizerAgent:
    name = "summarizer"

    def input_summary(self, ctx: PipelineContext) -> str:
        return f"{len(ctx.findings)} findings"

    async def run(self, ctx: PipelineContext) -> str:
        findings = [
            {"title": f.title, "body": f.body, "severity": f.severity.value}
            for f in ctx.findings
        ]
        user = prompts.summarizer_user(ctx.query, findings, ctx.risk_metrics)
        answer = await ctx.llm.complete(prompts.SUMMARIZER_SYSTEM, user)
        if not isinstance(answer, str):
            answer = str(answer)
        ctx.answer = answer.strip()
        return f"answer with {len(ctx.answer)} chars"
