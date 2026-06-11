"""Orchestrator: runs the agent pipeline in order and records a full execution trace.

Persists an AgentRun with a per-step trace and publishes lifecycle events. A step
failure marks the run failed with a clear error. A run never reports success it did not
actually achieve.
"""

from __future__ import annotations

import logging
from time import perf_counter

from app.agents.base import PipelineContext
from app.agents.insight import InsightAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.risk import RiskAgent
from app.agents.summarizer import SummarizerAgent
from app.core.ids import new_id, now_iso
from app.infra.events.base import EventPublisher
from app.infra.llm.base import LLMClient
from app.infra.repo.base import Repository
from app.schemas.agents import AgentRun, AgentStep
from app.schemas.common import RunStatus, StepStatus
from app.schemas.entities import Holding, Portfolio, Transaction

logger = logging.getLogger("quantastica.orchestrator")


class Orchestrator:
    def __init__(
        self, repository: Repository, llm: LLMClient, events: EventPublisher, retries: int
    ):
        self._repo = repository
        self._llm = llm
        self._events = events
        self._retries = retries

    async def run(
        self,
        user_id: str,
        portfolio: Portfolio,
        holdings: list[Holding],
        transactions: list[Transaction],
        query: str,
    ) -> AgentRun:
        run = AgentRun(
            id=new_id("run"),
            portfolio_id=portfolio.id,
            query=query,
            status=RunStatus.running,
            steps=[],
            findings=[],
            metrics=[],
            answer=None,
            error=None,
            created_at=now_iso(),
            completed_at=None,
        )
        await self._repo.create_run(user_id, run)
        await self._events.publish("run.started", {"runId": run.id, "portfolioId": portfolio.id})

        ctx = PipelineContext(
            run_id=run.id,
            query=query,
            portfolio=portfolio,
            holdings=holdings,
            transactions=transactions,
            llm=self._llm,
        )
        agents = [
            PlannerAgent(self._retries),
            ResearcherAgent(),
            RiskAgent(),
            InsightAgent(self._retries),
            SummarizerAgent(),
        ]

        for agent in agents:
            step = AgentStep(
                name=agent.name,
                status=StepStatus.running,
                input_summary=agent.input_summary(ctx),
                output_summary="",
                duration_ms=0.0,
                error=None,
            )
            start = perf_counter()
            try:
                output = await agent.run(ctx)
            except Exception as exc:  # any step failure fails the run
                step.status = StepStatus.failed
                step.error = str(exc)
                step.duration_ms = round((perf_counter() - start) * 1000, 3)
                run.steps.append(step)
                run.status = RunStatus.failed
                run.error = f"{agent.name} step failed: {exc}"
                run.completed_at = now_iso()
                self._sync(run, ctx)
                await self._repo.update_run(user_id, run)
                await self._events.publish(
                    "run.failed", {"runId": run.id, "step": agent.name, "error": str(exc)}
                )
                logger.warning("run %s failed at %s: %s", run.id, agent.name, exc)
                return run

            step.status = StepStatus.completed
            step.output_summary = output
            step.duration_ms = round((perf_counter() - start) * 1000, 3)
            run.steps.append(step)
            self._sync(run, ctx)
            if agent.name == "insight" and ctx.findings:
                await self._repo.add_findings(user_id, ctx.findings)
            await self._repo.update_run(user_id, run)
            await self._events.publish(
                "run.step_completed",
                {"runId": run.id, "step": agent.name, "durationMs": step.duration_ms},
            )

        run.status = RunStatus.completed
        run.completed_at = now_iso()
        self._sync(run, ctx)
        await self._repo.update_run(user_id, run)
        await self._events.publish(
            "run.completed", {"runId": run.id, "findings": len(run.findings)}
        )
        return run

    @staticmethod
    def _sync(run: AgentRun, ctx: PipelineContext) -> None:
        run.metrics = ctx.risk_metrics
        run.findings = ctx.findings
        run.answer = ctx.answer
