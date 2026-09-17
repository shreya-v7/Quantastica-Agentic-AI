"""Automation rule persistence and per-day execution counters."""

from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.ids import new_id
from app.infra.db.models import AutomationRuleRow
from app.schemas.automation import (
    AutomationAction,
    AutomationRule,
    AutomationTrigger,
    CreateAutomationRule,
)


class AutomationRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._sessions = session_factory

    async def create(self, user_id: str, req: CreateAutomationRule) -> AutomationRule:
        row = AutomationRuleRow(
            id=new_id("auto"),
            user_id=user_id,
            name=req.name,
            enabled=True,
            portfolio_id=req.portfolio_id,
            trigger=req.trigger.model_dump(by_alias=True),
            action=req.action.model_dump(by_alias=True),
            max_notional_inr=req.max_notional_inr,
            cooldown_seconds=req.cooldown_seconds,
            counter_date=date.today().isoformat(),
            created_at=datetime.now(UTC),
        )
        async with self._sessions() as session:
            session.add(row)
            await session.commit()
            await session.refresh(row)
        return self._rule(row)

    async def list(self, user_id: str) -> list[AutomationRule]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(AutomationRuleRow)
                    .where(AutomationRuleRow.user_id == user_id)
                    .order_by(AutomationRuleRow.created_at.desc())
                )
            ).all()
        return [self._rule(r) for r in rows]

    async def list_active_globally(self) -> list[AutomationRuleRow]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(AutomationRuleRow).where(AutomationRuleRow.enabled.is_(True))
                )
            ).all()
        return list(rows)

    async def set_enabled(self, user_id: str, rule_id: str, enabled: bool) -> None:
        async with self._sessions() as session:
            row = await session.get(AutomationRuleRow, rule_id)
            if row and row.user_id == user_id:
                row.enabled = enabled
                await session.commit()

    async def delete(self, user_id: str, rule_id: str) -> None:
        async with self._sessions() as session:
            row = await session.get(AutomationRuleRow, rule_id)
            if row and row.user_id == user_id:
                await session.delete(row)
                await session.commit()

    async def record_fire(self, rule_id: str, notional: float) -> None:
        today = date.today().isoformat()
        async with self._sessions() as session:
            row = await session.get(AutomationRuleRow, rule_id)
            if row is None:
                return
            if row.counter_date != today:
                row.counter_date = today
                row.executions_today = 0
                row.day_notional_inr = 0.0
            row.executions_today += 1
            row.day_notional_inr += notional
            row.last_fired_at = datetime.now(UTC)
            await session.commit()

    @staticmethod
    def _rule(row: AutomationRuleRow) -> AutomationRule:
        return AutomationRule(
            id=row.id,
            name=row.name,
            enabled=row.enabled,
            portfolio_id=row.portfolio_id,
            trigger=AutomationTrigger.model_validate(row.trigger),
            action=AutomationAction.model_validate(row.action),
            max_notional_inr=row.max_notional_inr,
            cooldown_seconds=row.cooldown_seconds,
            executions_today=row.executions_today,
            day_notional_inr=row.day_notional_inr,
            last_fired_at=row.last_fired_at.isoformat() if row.last_fired_at else None,
            created_at=row.created_at.isoformat(),
        )
