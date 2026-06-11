"""Portfolio read operations and metric computation."""

from __future__ import annotations

from app.agents.researcher import compute_metrics
from app.core.errors import NotFoundError
from app.infra.repo.base import Repository
from app.schemas.entities import Portfolio, PortfolioDetail


class PortfolioService:
    def __init__(self, repository: Repository):
        self._repo = repository

    async def list_portfolios(self, user_id: str) -> list[Portfolio]:
        return await self._repo.list_portfolios(user_id)

    async def get_detail(self, user_id: str, portfolio_id: str) -> PortfolioDetail:
        portfolio = await self._repo.get_portfolio(user_id, portfolio_id)
        if portfolio is None:
            raise NotFoundError(f"Portfolio '{portfolio_id}' not found")
        holdings = await self._repo.holdings_for(user_id, portfolio_id)
        metrics = compute_metrics(portfolio_id, holdings)
        return PortfolioDetail(portfolio=portfolio, holdings=holdings, metrics=metrics)
