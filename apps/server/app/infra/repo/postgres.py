"""PostgreSQL repository (SQLAlchemy 2 async + asyncpg)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.ids import new_id, now_iso
from app.infra.db.models import (
    AgentRunRow,
    CashAccountRow,
    CatalogProductRow,
    DebtRow,
    DepositRow,
    ExpenseRow,
    FindingRow,
    GoalRow,
    HoldingRow,
    IncomeProfileRow,
    InsurancePolicyRow,
    MfFolioRow,
    PortfolioRow,
    RetirementAccountRow,
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

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._sessions

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
            await session.execute(delete(CatalogProductRow).where(CatalogProductRow.seed.is_(True)))
            for product in bundle.catalog:
                await session.execute(
                    pg_insert(CatalogProductRow)
                    .values(
                        id=product["id"],
                        kind=product["kind"],
                        provider=product["provider"],
                        name=product["name"],
                        attributes=product["attributes"],
                        seed=product.get("seed", True),
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
            await _seed_profile(session, bundle.profile)
            await session.commit()
        return {
            "users": len(bundle.users),
            "portfolios": len(bundle.portfolios),
            "holdings": len(bundle.holdings),
            "transactions": len(bundle.transactions),
            "catalog": len(bundle.catalog),
            "profile": 1 if bundle.profile else 0,
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
                ("catalog", CatalogProductRow),
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


async def _seed_profile(session: AsyncSession, profile: dict) -> None:
    """Idempotently load the seed FinancialProfile. Existing seed rows for the user are
    cleared first so re-seeding without a reset stays consistent."""
    if not profile:
        return
    income = profile.get("income") or {}
    user_id = income.get("userId")
    if not user_id:
        return

    await session.execute(delete(IncomeProfileRow).where(IncomeProfileRow.user_id == user_id))
    session.add(
        IncomeProfileRow(
            user_id=user_id,
            basic_salary=income.get("basicSalary", 0.0),
            hra_received=income.get("hraReceived", 0.0),
            special_allowance=income.get("specialAllowance", 0.0),
            other_income=income.get("otherIncome", 0.0),
            rent_paid=income.get("rentPaid", 0.0),
            metro=income.get("metro", False),
            updated_at=datetime.fromisoformat(now_iso()),
        )
    )

    def add_all(items: list[dict], model, prefix: str, mapper) -> None:
        for item in items:
            session.add(model(id=new_id(prefix), user_id=user_id, seed=True, **mapper(item)))

    for model in (
        CashAccountRow, DepositRow, RetirementAccountRow, MfFolioRow,
        DebtRow, InsurancePolicyRow, ExpenseRow, GoalRow,
    ):
        await session.execute(delete(model).where(model.user_id == user_id, model.seed.is_(True)))

    add_all(
        profile.get("cashAccounts", []), CashAccountRow, "cash",
        lambda x: {"name": x["name"], "institution": x["institution"],
                   "balance_inr": x["balanceInr"]},
    )
    add_all(
        profile.get("deposits", []), DepositRow, "dep",
        lambda x: {"kind": x["kind"], "institution": x["institution"],
                   "principal_inr": x["principalInr"], "rate": x["rate"],
                   "maturity_date": x["maturityDate"]},
    )
    add_all(
        profile.get("retirementAccounts", []), RetirementAccountRow, "ret",
        lambda x: {"kind": x["kind"], "balance_inr": x["balanceInr"],
                   "annual_contribution_inr": x["annualContributionInr"]},
    )
    add_all(
        profile.get("mfFolios", []), MfFolioRow, "mf",
        lambda x: {"scheme_code": x["schemeCode"], "scheme_name": x["schemeName"],
                   "units": x["units"], "sip_amount_inr": x["sipAmountInr"],
                   "sip_day": x["sipDay"]},
    )
    add_all(
        profile.get("debts", []), DebtRow, "debt",
        lambda x: {"loan_type": x["loanType"], "lender": x["lender"],
                   "principal_outstanding_inr": x["principalOutstandingInr"], "rate": x["rate"],
                   "emi_inr": x["emiInr"], "tenure_months": x["tenureMonths"],
                   "annual_interest_inr": x.get("annualInterestInr", 0.0)},
    )
    add_all(
        profile.get("insurancePolicies", []), InsurancePolicyRow, "ins",
        lambda x: {"policy_type": x["policyType"], "provider": x["provider"],
                   "cover_inr": x["coverInr"], "annual_premium_inr": x["annualPremiumInr"],
                   "term_years": x.get("termYears", 0)},
    )
    add_all(
        profile.get("expenses", []), ExpenseRow, "exp",
        lambda x: {"category": x["category"], "monthly_inr": x["monthlyInr"]},
    )
    add_all(
        profile.get("goals", []), GoalRow, "goal",
        lambda x: {"name": x["name"], "target_inr": x["targetInr"],
                   "target_date": x["targetDate"], "priority": x.get("priority", "medium"),
                   "saved_inr": x.get("savedInr", 0.0)},
    )
