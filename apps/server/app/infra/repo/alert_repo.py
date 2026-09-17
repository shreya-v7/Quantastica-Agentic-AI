"""Price alert persistence."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.ids import new_id
from app.infra.db.models import AlertRow
from app.schemas.alert import Alert, CreateAlert
from app.schemas.common import AlertOperator


class AlertRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._sessions = session_factory

    async def create(self, user_id: str, req: CreateAlert) -> Alert:
        row = AlertRow(
            id=new_id("alert"),
            user_id=user_id,
            name=req.name,
            kind=req.kind,
            symbol=req.symbol,
            operator=req.operator.value,
            threshold=req.threshold,
            channel=req.channel,
            enabled=True,
            cooldown_seconds=req.cooldown_seconds,
            created_at=datetime.now(UTC),
        )
        async with self._sessions() as session:
            session.add(row)
            await session.commit()
            await session.refresh(row)
        return self._alert(row)

    async def list(self, user_id: str) -> list[Alert]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(AlertRow)
                    .where(AlertRow.user_id == user_id)
                    .order_by(AlertRow.created_at.desc())
                )
            ).all()
        return [self._alert(r) for r in rows]

    async def list_active_globally(self) -> list[AlertRow]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(select(AlertRow).where(AlertRow.enabled.is_(True)))
            ).all()
        return list(rows)

    async def set_enabled(self, user_id: str, alert_id: str, enabled: bool) -> None:
        async with self._sessions() as session:
            row = await session.get(AlertRow, alert_id)
            if row and row.user_id == user_id:
                row.enabled = enabled
                await session.commit()

    async def delete(self, user_id: str, alert_id: str) -> None:
        async with self._sessions() as session:
            row = await session.get(AlertRow, alert_id)
            if row and row.user_id == user_id:
                await session.delete(row)
                await session.commit()

    async def record_trigger(self, alert_id: str, label: str | None = None) -> None:
        async with self._sessions() as session:
            row = await session.get(AlertRow, alert_id)
            if row:
                row.last_triggered_at = datetime.now(UTC)
                if label is not None:
                    row.last_label = label
                await session.commit()

    async def record_label(self, alert_id: str, label: str) -> None:
        async with self._sessions() as session:
            row = await session.get(AlertRow, alert_id)
            if row:
                row.last_label = label
                await session.commit()

    @staticmethod
    def _alert(row: AlertRow) -> Alert:
        return Alert(
            id=row.id,
            name=row.name,
            kind=row.kind,
            symbol=row.symbol,
            operator=AlertOperator(row.operator),
            threshold=row.threshold,
            channel=row.channel,
            enabled=row.enabled,
            cooldown_seconds=row.cooldown_seconds,
            last_label=row.last_label,
            last_triggered_at=row.last_triggered_at.isoformat() if row.last_triggered_at else None,
            created_at=row.created_at.isoformat(),
        )
