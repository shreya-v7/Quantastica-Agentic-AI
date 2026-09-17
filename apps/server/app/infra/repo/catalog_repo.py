"""Read access to the global loan/insurance product catalog (reference data)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infra.db.models import CatalogProductRow


class CatalogRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._sessions = session_factory

    async def list_by_kind(self, kind: str) -> list[CatalogProductRow]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(CatalogProductRow)
                    .where(CatalogProductRow.kind == kind)
                    .order_by(CatalogProductRow.provider)
                )
            ).all()
        return list(rows)
