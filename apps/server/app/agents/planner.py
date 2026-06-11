"""Planner agent: one LLM call producing a validated JSON plan."""

from __future__ import annotations

from app.agents import prompts
from app.agents.base import PipelineContext
from app.agents.llm_json import complete_json
from app.schemas.agents import Plan


class PlannerAgent:
    name = "planner"

    def __init__(self, retries: int):
        self._retries = retries

    def input_summary(self, ctx: PipelineContext) -> str:
        return f"query='{ctx.query}', portfolio={ctx.portfolio.id}"

    async def run(self, ctx: PipelineContext) -> str:
        preview = {
            "holdings": len(ctx.holdings),
            "transactions": len(ctx.transactions),
            "symbols": [h.symbol for h in ctx.holdings],
        }
        user = prompts.planner_user(ctx.query, ctx.portfolio, preview)
        plan = await complete_json(
            ctx.llm, prompts.PLANNER_SYSTEM, user, Plan, self._retries
        )
        ctx.plan = plan
        return f"plan with {len(plan.steps)} steps: {[s.analysis for s in plan.steps]}"
