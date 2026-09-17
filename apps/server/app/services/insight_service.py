"""Insight read operations."""

from __future__ import annotations

from app.infra.repo.base import Repository
from app.schemas.agents import Finding
from app.schemas.common import Severity


class InsightService:
    def __init__(self, repository: Repository):
        self._repo = repository

    async def list_insights(
        self,
        user_id: str,
        portfolio_id: str | None = None,
        severity: Severity | None = None,
    ) -> list[Finding]:
        return await self._repo.list_insights(
            user_id, portfolio_id=portfolio_id, severity=severity
        )
