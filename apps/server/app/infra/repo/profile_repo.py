"""FinancialProfile persistence. Every read and write is scoped by user id. The income
row is a singleton upsert; the other categories are append/delete collections."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.ids import new_id
from app.infra.db.models import (
    CashAccountRow,
    DebtRow,
    DepositRow,
    ExpenseRow,
    GoalRow,
    IncomeProfileRow,
    InsurancePolicyRow,
    MfFolioRow,
    RetirementAccountRow,
)

_COLLECTIONS = {
    "cash_accounts": CashAccountRow,
    "deposits": DepositRow,
    "retirement_accounts": RetirementAccountRow,
    "mf_folios": MfFolioRow,
    "debts": DebtRow,
    "insurance_policies": InsurancePolicyRow,
    "expenses": ExpenseRow,
    "goals": GoalRow,
}

_PREFIXES = {
    "cash_accounts": "cash",
    "deposits": "dep",
    "retirement_accounts": "ret",
    "mf_folios": "mf",
    "debts": "debt",
    "insurance_policies": "ins",
    "expenses": "exp",
    "goals": "goal",
}


class ProfileRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._sessions = session_factory

    async def get_income(self, user_id: str) -> IncomeProfileRow | None:
        async with self._sessions() as session:
            return await session.get(IncomeProfileRow, user_id)

    async def upsert_income(self, user_id: str, values: dict) -> IncomeProfileRow:
        async with self._sessions() as session:
            row = await session.get(IncomeProfileRow, user_id)
            if row is None:
                row = IncomeProfileRow(user_id=user_id, updated_at=datetime.now(UTC))
                session.add(row)
            for key, value in values.items():
                setattr(row, key, value)
            row.updated_at = datetime.now(UTC)
            await session.commit()
            await session.refresh(row)
            return row

    async def list_all(self, user_id: str, collection: str) -> list:
        model = _COLLECTIONS[collection]
        async with self._sessions() as session:
            rows = (
                await session.scalars(select(model).where(model.user_id == user_id))
            ).all()
        return list(rows)

    async def add(self, user_id: str, collection: str, values: dict) -> object:
        model = _COLLECTIONS[collection]
        row = model(id=new_id(_PREFIXES[collection]), user_id=user_id, **values)
        async with self._sessions() as session:
            session.add(row)
            await session.commit()
            await session.refresh(row)
        return row

    async def delete(self, user_id: str, collection: str, item_id: str) -> bool:
        model = _COLLECTIONS[collection]
        async with self._sessions() as session:
            row = await session.get(model, item_id)
            if row is None or row.user_id != user_id:
                return False
            await session.delete(row)
            await session.commit()
            return True

    async def clear_seed(self, session: AsyncSession) -> None:
        await session.execute(delete(IncomeProfileRow))
        for model in _COLLECTIONS.values():
            await session.execute(delete(model).where(model.seed.is_(True)))
