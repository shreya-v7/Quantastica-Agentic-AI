"""Ingest HTTP: parse, review, apply. Missing fields pause. No silent defaults."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.dependencies import get_container
from app.core.envelope import success
from app.core.errors import NotFoundError
from app.infra.factory import Container
from app.infra.repo.book_repo import BookRepository
from app.infra.repo.ingest_repo import IngestRepository
from app.ingest.service import IngestService
from app.services.desk_service import DeskService

router = APIRouter(prefix="/ingest")


def _service(container: Container) -> IngestService:
    books = BookRepository(container.session_factory)
    return IngestService(
        books,
        DeskService(books),
        IngestRepository(container.session_factory),
    )


class IngestBody(BaseModel):
    household_id: str
    kind: str = "text_event"
    raw_text: str = ""
    image_b64: str | None = None
    vlm_override: dict | None = None


class ResumeBody(BaseModel):
    thread_id: str
    patch: dict = Field(default_factory=dict)


@router.post("")
async def ingest(body: IngestBody, container: Container = Depends(get_container)) -> dict:
    service = _service(container)
    state = service.parse(
        {
            "household_id": body.household_id,
            "kind": body.kind,
            "raw_text": body.raw_text,
            "image_b64": body.image_b64,
            "vlm_override": body.vlm_override,
        }
    )
    return success(await service.apply(body.household_id, state))


@router.post("/resume")
async def resume(body: ResumeBody, container: Container = Depends(get_container)) -> dict:
    service = _service(container)
    try:
        state = await service.resume(body.thread_id, body.patch)
    except KeyError as exc:
        raise NotFoundError(f"Paused ingest {body.thread_id} not found") from exc
    household_id = str(state.get("household_id") or "")
    return success(await service.apply(household_id, state))
