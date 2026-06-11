"""PostgreSQL repository (SQLAlchemy 2 async + asyncpg)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infra.db.models import (
    AgentRunRow,
    FindingRow,
    HoldingRow,
    PortfolioRow,
    TransactionRow,
    UserRow,
)
from app.infra.repo.base import Repository, SeedBundle
from app.schemas.agents import AgentRun, Finding
from app.schemas.common import Severity
from app.schemas.entities import Holding, Portfolio, Transaction


class PostgresRepository(Repository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._sessions = session_factory

    # --- portfolios ---------------------------------------------------------
    async def list_portfolios(self, user_id: str) -> list[Portfolio]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(PortfolioRow)
                    .where(PortfolioRow.user_id == user_id)
                    .order_by(PortfolioRow.name)
                )
            ).all()
        return [self._portfolio(r) for r in rows]

    async def get_portfolio(self, user_id: str, portfolio_id: str) -> Portfolio | None:
        async with self._sessions() as session:
            row = await session.scalar(
                select(PortfolioRow).where(
                    PortfolioRow.user_id == user_id, PortfolioRow.id == portfolio_id
                )
            )
        return self._portfolio(row) if row else None

    async def holdings_for(self, user_id: str, portfolio_id: str) -> list[Holding]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(HoldingRow)
                    .where(
                        HoldingRow.user_id == user_id,
                        HoldingRow.portfolio_id == portfolio_id,
                    )
                    .order_by(HoldingRow.symbol)
                )
            ).all()
        return [self._holding(r) for r in rows]

    async def transactions_for(self, user_id: str, portfolio_id: str) -> list[Transaction]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(TransactionRow)
                    .where(
                        TransactionRow.user_id == user_id,
                        TransactionRow.portfolio_id == portfolio_id,
                    )
                    .order_by(TransactionRow.timestamp)
                )
            ).all()
        return [self._transaction(r) for r in rows]

    # --- insights -----------------------------------------------------------
    async def list_insights(
        self,
        user_id: str,
        portfolio_id: str | None = None,
        severity: Severity | None = None,
    ) -> list[Finding]:
        stmt = select(FindingRow).where(FindingRow.user_id == user_id)
        if portfolio_id:
            stmt = stmt.where(FindingRow.portfolio_id == portfolio_id)
        if severity:
            stmt = stmt.where(FindingRow.severity == severity.value)
        stmt = stmt.order_by(FindingRow.created_at.desc())
        async with self._sessions() as session:
            rows = (await session.scalars(stmt)).all()
        return [self._finding(r) for r in rows]

    async def add_findings(self, user_id: str, findings: list[Finding]) -> None:
        async with self._sessions() as session:
            for f in findings:
                await session.execute(
                    pg_insert(FindingRow)
                    .values(
                        id=f.id,
                        user_id=user_id,
                        portfolio_id=f.portfolio_id,
                        run_id=f.run_id,
                        title=f.title,
                        body=f.body,
                        severity=f.severity.value,
                        confidence=f.confidence,
                        metric_ids=f.metric_ids,
                        created_at=f.created_at,
                        seed=f.seed,
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
            await session.commit()

    # --- runs ---------------------------------------------------------------
    async def create_run(self, user_id: str, run: AgentRun) -> None:
        await self._upsert_run(user_id, run)

    async def update_run(self, user_id: str, run: AgentRun) -> None:
        await self._upsert_run(user_id, run)

    async def get_run(self, user_id: str, run_id: str) -> AgentRun | None:
        async with self._sessions() as session:
            row = await session.scalar(
                select(AgentRunRow).where(
                    AgentRunRow.user_id == user_id, AgentRunRow.id == run_id
                )
            )
        return AgentRun.model_validate(row.data) if row else None

    async def list_runs(
        self, user_id: str, portfolio_id: str | None = None
    ) -> list[AgentRun]:
        stmt = select(AgentRunRow).where(AgentRunRow.user_id == user_id)
        if portfolio_id:
            stmt = stmt.where(AgentRunRow.portfolio_id == portfolio_id)
        stmt = stmt.order_by(AgentRunRow.created_at.desc())
        async with self._sessions() as session:
            rows = (await session.scalars(stmt)).all()
        return [AgentRun.model_validate(r.data) for r in rows]

    async def _upsert_run(self, user_id: str, run: AgentRun) -> None:
        data = run.model_dump(mode="json", by_alias=True)
        async with self._sessions() as session:
            stmt = pg_insert(AgentRunRow).values(
                id=run.id,
                user_id=user_id,
                portfolio_id=run.portfolio_id,
                created_at=run.created_at,
                data=data,
            )
            await session.execute(
                stmt.on_conflict_do_update(index_elements=["id"], set_={"data": data})
            )
            await session.commit()

    # --- seed ---------------------------------------------------------------
    async def load_seed(self, bundle: SeedBundle) -> dict[str, int]:
        async with self._sessions() as session:
            await session.execute(delete(UserRow).where(UserRow.seed.is_(True)))
            for user in bundle.users:
                await session.execute(
                    pg_insert(UserRow)
                    .values(
                        id=user["id"],
                        email=user.get("email"),
                        role=user.get("role", "user"),
                        phone=user.get("phone"),
                        phone_verified=user.get("phoneVerified", False),
                        created_at=datetime.fromisoformat(user["createdAt"]),
                        seed=True,
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
            for p in bundle.portfolios:
                await session.execute(
                    pg_insert(PortfolioRow)
                    .values(
                        id=p.id,
                        user_id=bundle.owner_by_portfolio[p.id],
                        name=p.name,
                        base_currency=p.base_currency,
                        created_at=datetime.fromisoformat(p.created_at),
                        seed=p.seed,
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
            for h in bundle.holdings:
                await session.execute(
                    pg_insert(HoldingRow)
                    .values(
                        id=h.id,
                        user_id=bundle.owner_by_portfolio[h.portfolio_id],
                        portfolio_id=h.portfolio_id,
                        symbol=h.symbol,
                        name=h.name,
                        asset_class=h.asset_class.value,
                        sector=h.sector,
                        quantity=h.quantity,
                        cost_basis=h.cost_basis,
                        current_price=h.current_price,
                        seed=h.seed,
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
            for t in bundle.transactions:
                await session.execute(
                    pg_insert(TransactionRow)
                    .values(
                        id=t.id,
                        user_id=bundle.owner_by_portfolio[t.portfolio_id],
                        portfolio_id=t.portfolio_id,
                        symbol=t.symbol,
                        type=t.type.value,
                        quantity=t.quantity,
                        price=t.price,
                        timestamp=t.timestamp,
                        seed=t.seed,
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
            await session.commit()
        return {
            "users": len(bundle.users),
            "portfolios": len(bundle.portfolios),
            "holdings": len(bundle.holdings),
            "transactions": len(bundle.transactions),
        }

    async def reset_seed(self) -> dict[str, int]:
        async with self._sessions() as session:
            seed_users = (
                await session.scalars(select(UserRow.id).where(UserRow.seed.is_(True)))
            ).all()
            counts: dict[str, int] = {}
            for name, model in (
                ("findings", FindingRow),
                ("transactions", TransactionRow),
                ("holdings", HoldingRow),
                ("portfolios", PortfolioRow),
            ):
                result = await session.execute(delete(model).where(model.seed.is_(True)))
                counts[name] = result.rowcount or 0
            if seed_users:
                await session.execute(
                    delete(AgentRunRow).where(AgentRunRow.user_id.in_(seed_users))
                )
                result = await session.execute(delete(UserRow).where(UserRow.seed.is_(True)))
                counts["users"] = result.rowcount or 0
            else:
                counts["users"] = 0
            await session.commit()
        return counts

    # --- row mappers --------------------------------------------------------
    @staticmethod
    def _portfolio(row: PortfolioRow) -> Portfolio:
        return Portfolio(
            id=row.id,
            name=row.name,
            base_currency=row.base_currency,
            created_at=row.created_at.isoformat(),
            seed=row.seed,
        )

    @staticmethod
    def _holding(row: HoldingRow) -> Holding:
        return Holding(
            id=row.id,
            portfolio_id=row.portfolio_id,
            symbol=row.symbol,
            name=row.name,
            asset_class=row.asset_class,
            sector=row.sector,
            quantity=float(row.quantity),
            cost_basis=float(row.cost_basis),
            current_price=float(row.current_price),
            seed=row.seed,
        )

    @staticmethod
    def _transaction(row: TransactionRow) -> Transaction:
        return Transaction(
            id=row.id,
            portfolio_id=row.portfolio_id,
            symbol=row.symbol,
            type=row.type,
            quantity=float(row.quantity),
            price=float(row.price),
            timestamp=row.timestamp,
            seed=row.seed,
        )

    @staticmethod
    def _finding(row: FindingRow) -> Finding:
        return Finding(
            id=row.id,
            portfolio_id=row.portfolio_id,
            run_id=row.run_id,
            title=row.title,
            body=row.body,
            severity=row.severity,
            confidence=row.confidence,
            metric_ids=list(row.metric_ids),
            created_at=row.created_at,
            seed=row.seed,
        )
