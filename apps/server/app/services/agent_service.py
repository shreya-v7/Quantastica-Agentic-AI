"""Agent run orchestration entry point and run export."""

from __future__ import annotations

from app.agents.orchestrator import Orchestrator
from app.core.errors import NotFoundError
from app.infra.factory import Container
from app.schemas.agents import AgentRun, ExportResult


class AgentService:
    def __init__(self, container: Container):
        self._container = container
        self._repo = container.repository

    async def run(self, user_id: str, query: str, portfolio_id: str) -> AgentRun:
        portfolio = await self._repo.get_portfolio(user_id, portfolio_id)
        if portfolio is None:
            raise NotFoundError(f"Portfolio '{portfolio_id}' not found")
        holdings = await self._repo.holdings_for(user_id, portfolio_id)
        transactions = await self._repo.transactions_for(user_id, portfolio_id)

        orchestrator = Orchestrator(
            repository=self._repo,
            llm=self._container.llm,
            events=self._container.events,
            retries=self._container.settings.llm_retries,
            retriever=self._retrieve,
        )
        return await orchestrator.run(user_id, portfolio, holdings, transactions, query)

    async def _retrieve(self, user_id: str, query: str):
        from app.core.errors import ProviderNotConfiguredError
        from app.services.document_service import DocumentService

        try:
            return await DocumentService(self._container).retrieve_passages(user_id, query, k=5)
        except ProviderNotConfiguredError:
            return []

    async def list_runs(self, user_id: str, portfolio_id: str | None = None) -> list[AgentRun]:
        return await self._repo.list_runs(user_id, portfolio_id=portfolio_id)

    async def get_run(self, user_id: str, run_id: str) -> AgentRun:
        run = await self._repo.get_run(user_id, run_id)
        if run is None:
            raise NotFoundError(f"Run '{run_id}' not found")
        return run

    async def export_run(self, user_id: str, run_id: str) -> ExportResult:
        run = await self.get_run(user_id, run_id)
        data = run.model_dump_json(by_alias=True, indent=2).encode("utf-8")
        location = await self._container.storage.put(
            f"runs/{run_id}.json", data, "application/json"
        )
        return ExportResult(run_id=run_id, location=location, content_type="application/json")
