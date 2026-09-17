"""Orchestrator: LangGraph control flow over grounded agents, with a full execution trace.

Planner, Researcher, Retrieve, Risk, Insight, Summarizer run as graph nodes. Researcher
and Risk are pure code. Retrieve is hybrid RAG. A step failure marks the run failed with
a clear error. A run never reports success it did not actually achieve.
"""

from __future__ import annotations

import logging
from time import perf_counter

from langgraph.graph import END, StateGraph

from app.agents.base import PipelineContext
from app.agents.graph_state import GraphState
from app.agents.insight import InsightAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.retrieve import RetrieveAgent, Retriever
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

PIPELINE = ("planner", "researcher", "retrieve", "risk", "insight", "summarizer")


class Orchestrator:
    def __init__(
        self,
        repository: Repository,
        llm: LLMClient,
        events: EventPublisher,
        retries: int,
        retriever: Retriever | None = None,
    ):
        self._repo = repository
        self._llm = llm
        self._events = events
        self._retries = retries
        self._retriever = retriever

    def _agents(self) -> dict[str, object]:
        agents = [
            PlannerAgent(self._retries),
            ResearcherAgent(),
            RetrieveAgent(self._retriever),
            RiskAgent(),
            InsightAgent(self._retries),
            SummarizerAgent(),
        ]
        return {agent.name: agent for agent in agents}

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
            user_id=user_id,
            query=query,
            portfolio=portfolio,
            holdings=holdings,
            transactions=transactions,
            llm=self._llm,
        )
        graph = self._compile(user_id, run, ctx)
        await graph.ainvoke({"failed": False})
        return run

    def _compile(self, user_id: str, run: AgentRun, ctx: PipelineContext):
        agents = self._agents()
        builder = StateGraph(GraphState)

        def bind(name: str):
            async def node(state: GraphState) -> GraphState:
                if state.get("failed"):
                    return state
                failed = await self._run_step(user_id, run, ctx, agents[name])
                return {"failed": failed, "last_step": name}

            node.__name__ = f"{name}_node"
            return node

        for name in PIPELINE:
            builder.add_node(name, bind(name))
        builder.set_entry_point(PIPELINE[0])
        for left, right in zip(PIPELINE[:-1], PIPELINE[1:], strict=True):
            builder.add_edge(left, right)
        builder.add_edge(PIPELINE[-1], END)
        return builder.compile()

    async def _run_step(self, user_id: str, run: AgentRun, ctx: PipelineContext, agent) -> bool:
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
        except Exception as exc:
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
            return True

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

        if agent.name == PIPELINE[-1]:
            run.status = RunStatus.completed
            run.completed_at = now_iso()
            self._sync(run, ctx)
            await self._repo.update_run(user_id, run)
            await self._events.publish(
                "run.completed", {"runId": run.id, "findings": len(run.findings)}
            )
        return False

    @staticmethod
    def _sync(run: AgentRun, ctx: PipelineContext) -> None:
        run.metrics = ctx.risk_metrics
        run.findings = ctx.findings
        run.answer = ctx.answer
