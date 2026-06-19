"""FinancialProfile endpoints (Phase A). GET assembles the full aggregate with net worth;
income is a singleton PUT; the other categories are add/delete collections. All scoped to
the authenticated user."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.dependencies import current_user_id, get_container
from app.core.envelope import success
from app.core.errors import NotFoundError, ValidationError
from app.infra.factory import Container
from app.infra.repo.profile_repo import ProfileRepository
from app.schemas.profile import (
    CreateCashAccount,
    CreateDebt,
    CreateDeposit,
    CreateExpense,
    CreateGoal,
    CreateInsurancePolicy,
    CreateMfFolio,
    CreateRetirementAccount,
    IncomeProfile,
)
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile")

# Public path segment -> repository collection key (used by the generic delete route).
_SEGMENTS = {
    "cash-accounts": "cash_accounts",
    "deposits": "deposits",
    "retirement-accounts": "retirement_accounts",
    "mf-folios": "mf_folios",
    "debts": "debts",
    "insurance-policies": "insurance_policies",
    "expenses": "expenses",
    "goals": "goals",
}


def _repo(container: Container) -> ProfileRepository:
    return ProfileRepository(container.session_factory)


@router.get("")
async def get_profile(
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return success(await ProfileService(container).get_profile(user_id))


@router.put("/income")
async def set_income(
    body: IncomeProfile,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return success(await ProfileService(container).set_income(user_id, body))


async def _add(container: Container, user_id: str, collection: str, body) -> dict:
    row = await _repo(container).add(user_id, collection, body.model_dump())
    return success({"id": row.id})


@router.post("/cash-accounts")
async def add_cash(
    body: CreateCashAccount,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return await _add(container, user_id, "cash_accounts", body)


@router.post("/deposits")
async def add_deposit(
    body: CreateDeposit,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return await _add(container, user_id, "deposits", body)


@router.post("/retirement-accounts")
async def add_retirement(
    body: CreateRetirementAccount,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return await _add(container, user_id, "retirement_accounts", body)


@router.post("/mf-folios")
async def add_folio(
    body: CreateMfFolio,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return await _add(container, user_id, "mf_folios", body)


@router.post("/debts")
async def add_debt(
    body: CreateDebt,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return await _add(container, user_id, "debts", body)


@router.post("/insurance-policies")
async def add_insurance(
    body: CreateInsurancePolicy,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return await _add(container, user_id, "insurance_policies", body)


@router.post("/expenses")
async def add_expense(
    body: CreateExpense,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return await _add(container, user_id, "expenses", body)


@router.post("/goals")
async def add_goal(
    body: CreateGoal,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return await _add(container, user_id, "goals", body)


@router.delete("/{segment}/{item_id}")
async def delete_item(
    segment: str,
    item_id: str,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    collection = _SEGMENTS.get(segment)
    if collection is None:
        raise ValidationError(f"Unknown profile collection '{segment}'")
    if not await _repo(container).delete(user_id, collection, item_id):
        raise NotFoundError(f"{segment} item '{item_id}' not found")
    return success({"id": item_id, "deleted": True})
