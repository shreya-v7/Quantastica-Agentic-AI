"""Repository interface. PostgreSQL is the single store on every platform.

Every read and write is scoped by user_id at the query level (authorization happens
here, not only in routes). The interface is async end to end.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.agents import AgentRun, Finding
from app.schemas.common import Severity
from app.schemas.entities import Holding, Portfolio, Transaction


class Repository(ABC):
    @abstractmethod
    async def list_portfolios(self, user_id: str) -> list[Portfolio]: ...

    @abstractmethod
    async def get_portfolio(self, user_id: str, portfolio_id: str) -> Portfolio | None: ...

    @abstractmethod
    async def holdings_for(self, user_id: str, portfolio_id: str) -> list[Holding]: ...

    @abstractmethod
    async def transactions_for(self, user_id: str, portfolio_id: str) -> list[Transaction]: ...

    @abstractmethod
    async def list_insights(
        self,
        user_id: str,
        portfolio_id: str | None = None,
        severity: Severity | None = None,
    ) -> list[Finding]: ...

    @abstractmethod
    async def add_findings(self, user_id: str, findings: list[Finding]) -> None: ...

    @abstractmethod
    async def create_run(self, user_id: str, run: AgentRun) -> None: ...

    @abstractmethod
    async def update_run(self, user_id: str, run: AgentRun) -> None: ...

    @abstractmethod
    async def get_run(self, user_id: str, run_id: str) -> AgentRun | None: ...

    @abstractmethod
    async def list_runs(
        self, user_id: str, portfolio_id: str | None = None
    ) -> list[AgentRun]: ...

    @abstractmethod
    async def load_seed(self, bundle: SeedBundle) -> dict[str, int]: ...

    @abstractmethod
    async def reset_seed(self) -> dict[str, int]: ...


class SeedBundle:
    """Container for flagged seed records, populated by app.seed.loader only."""

    def __init__(
        self,
        users: list[dict],
        portfolios: list[Portfolio],
        holdings: list[Holding],
        transactions: list[Transaction],
        owner_by_portfolio: dict[str, str],
    ):
        self.users = users
        self.portfolios = portfolios
        self.holdings = holdings
        self.transactions = transactions
        self.owner_by_portfolio = owner_by_portfolio
