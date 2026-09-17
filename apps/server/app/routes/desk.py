"""Exception desk: household queue, traces, lot mutations."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.dependencies import get_container
from app.core.envelope import success
from app.core.errors import NotFoundError, ValidationError
from app.infra.factory import Container
from app.infra.repo.book_repo import BookRepository
from app.services.desk_service import DeskService

router = APIRouter(prefix="/desk")


def _desk(container: Container) -> DeskService:
    return DeskService(BookRepository(container.session_factory))


@router.get("/households")
async def households(container: Container = Depends(get_container)) -> dict:
    return success(await _desk(container).households())


@router.get("/households/{household_id}/queue")
async def queue(household_id: str, container: Container = Depends(get_container)) -> dict:
    return success(await _desk(container).queue(household_id))


@router.get("/exceptions/{exception_id}")
async def exception(exception_id: str, container: Container = Depends(get_container)) -> dict:
    return success(await _desk(container).exception(exception_id))


class LotQuantityBody(BaseModel):
    quantity: float = Field(ge=0, allow_inf_nan=False)
    valid_time: datetime | None = None
    idempotency_key: str | None = Field(default=None, max_length=60)


@router.post("/households/{household_id}/lots/{lot_id}")
async def set_lot(
    household_id: str,
    lot_id: str,
    body: LotQuantityBody,
    container: Container = Depends(get_container),
) -> dict:
    return success(await _desk(container).set_lot_quantity(
        household_id, lot_id, body.quantity, body.valid_time, body.idempotency_key
    ))


@router.post("/households/{household_id}/recompute")
async def recompute(household_id: str, container: Container = Depends(get_container)) -> dict:
    diff = await _desk(container).recompute(household_id)
    return success(diff)


@router.get("/households/{household_id}/as-of")
async def as_of(household_id: str, valid_time: datetime, recorded_time: datetime,
                container: Container = Depends(get_container)) -> dict:
    try:
        book = await BookRepository(container.session_factory).as_of(
            household_id, valid_time, recorded_time)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc
    if book is None:
        raise NotFoundError("No household state known at the requested times")
    return success(book)


@router.get("/households/{household_id}/history")
async def history(household_id: str, container: Container = Depends(get_container)) -> dict:
    return success(await BookRepository(container.session_factory).history(household_id))
