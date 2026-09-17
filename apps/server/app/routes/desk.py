"""Exception desk: household queue, traces, lot mutations."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.dependencies import get_container
from app.core.envelope import success
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
    quantity: float = Field(ge=0)


@router.post("/households/{household_id}/lots/{lot_id}")
async def set_lot(
    household_id: str,
    lot_id: str,
    body: LotQuantityBody,
    container: Container = Depends(get_container),
) -> dict:
    return success(await _desk(container).set_lot_quantity(household_id, lot_id, body.quantity))


@router.post("/households/{household_id}/recompute")
async def recompute(household_id: str, container: Container = Depends(get_container)) -> dict:
    diff = await _desk(container).recompute(household_id)
    return success(diff)
