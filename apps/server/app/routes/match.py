"""Loan and insurance matching endpoints (Phase E). Scoring is deterministic; results
carry per-product eligibility reasons and INR display strings."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.dependencies import current_user_id, get_container
from app.core.envelope import success
from app.infra.factory import Container
from app.infra.repo.catalog_repo import CatalogRepository
from app.services.match_service import (
    InsuranceMatchRequest,
    LoanMatchRequest,
    MatchService,
)

router = APIRouter(prefix="/match")


def _service(container: Container) -> MatchService:
    return MatchService(CatalogRepository(container.session_factory))


@router.post("/loans")
async def match_loans(
    body: LoanMatchRequest,
    _: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return success(await _service(container).match_loans(body))


@router.post("/insurance")
async def match_insurance(
    body: InsuranceMatchRequest,
    _: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return success(await _service(container).match_insurance(body))
