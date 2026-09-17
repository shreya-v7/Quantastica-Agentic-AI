"""Persist ingest artifacts and paused LangGraph threads."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.ids import new_id
from app.infra.db.models import (
    ConsentRow,
    ExceptionRow,
    GraphCheckpointRow,
    HouseholdRow,
    IngestArtifactRow,
    LotRow,
)


class IngestRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._sessions = session_factory

    async def save_checkpoint(self, thread_id: str, state: dict) -> None:
        async with self._sessions() as session:
            row = await session.get(GraphCheckpointRow, thread_id)
            now = datetime.now(UTC)
            if row is None:
                session.add(
                    GraphCheckpointRow(thread_id=thread_id, state=dict(state), updated_at=now)
                )
            else:
                row.state = dict(state)
                row.updated_at = now
            await session.commit()

    async def load_checkpoint(self, thread_id: str) -> dict | None:
        async with self._sessions() as session:
            row = await session.get(GraphCheckpointRow, thread_id)
        if row is None:
            return None
        return dict(row.state)  # type: ignore[return-value]

    async def save_artifact(
        self,
        household_id: str,
        kind: str,
        status: str,
        extracted: dict | None,
        missing_fields: list[str],
        confidence: float,
        thread_id: str | None = None,
    ) -> str:
        artifact_id = new_id("ing")
        async with self._sessions() as session:
            session.add(
                IngestArtifactRow(
                    id=artifact_id,
                    household_id=household_id,
                    kind=kind,
                    status=status,
                    extracted=extracted,
                    missing_fields=missing_fields,
                    confidence=confidence,
                    thread_id=thread_id,
                    created_at=datetime.now(UTC),
                )
            )
            await session.commit()
        return artifact_id

    async def add_consent(self, household_id: str, purpose: str, granted: bool = True) -> str:
        consent_id = new_id("cns")
        async with self._sessions() as session:
            session.add(
                ConsentRow(
                    id=consent_id,
                    household_id=household_id,
                    purpose=purpose,
                    granted=granted,
                    created_at=datetime.now(UTC),
                )
            )
            await session.commit()
        return consent_id

    async def list_consents(self, household_id: str) -> list[dict]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(ConsentRow)
                    .where(ConsentRow.household_id == household_id)
                    .order_by(ConsentRow.created_at.desc())
                )
            ).all()
        return [
            {
                "id": row.id,
                "householdId": row.household_id,
                "purpose": row.purpose,
                "granted": row.granted,
                "createdAt": row.created_at.isoformat(),
            }
            for row in rows
        ]

    async def metrics(self) -> dict:
        async with self._sessions() as session:
            households = (
                await session.scalar(select(func.count()).select_from(HouseholdRow)) or 0
            )
            lots = await session.scalar(select(func.count()).select_from(LotRow)) or 0
            artifacts = (
                await session.scalar(select(func.count()).select_from(IngestArtifactRow)) or 0
            )
            exceptions = await session.scalar(
                select(func.count()).select_from(ExceptionRow).where(ExceptionRow.status == "open")
            ) or 0
            rupee = await session.scalar(
                select(func.coalesce(func.sum(ExceptionRow.rupee_delta), 0)).where(
                    ExceptionRow.status == "open"
                )
            ) or 0
        return {
            "households": int(households),
            "lots": int(lots),
            "documentsIngested": int(artifacts),
            "exceptionsOpen": int(exceptions),
            "rupeeDeltaSurfaced": float(rupee),
            "reviewRate": 0.0,
            "extractionAccuracy": None,
            "medianUploadToExceptionSeconds": None,
        }
