"""Feature flags, DPDP export, pitch metrics, scripted demo."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.dependencies import get_container, require_role
from app.core.envelope import success
from app.infra.factory import Container
from app.infra.repo.book_repo import BookRepository
from app.infra.repo.ingest_repo import IngestRepository
from app.ingest.extractors import FORM16_FIXTURE
from app.ingest.service import IngestService
from app.privacy import mask_pii
from app.services.desk_service import DeskService
from app.speech.provider import queue_script

router = APIRouter()


@router.get("/flags")
def flags(container: Container = Depends(get_container)) -> dict:
    settings = container.settings
    return success(
        {
            "tradingChat": settings.trading_chat_enabled,
            "tradingMode": settings.trading_mode,
            "voice": settings.voice_enabled,
            "demoMode": settings.demo_mode,
            "roles": ["admin", "adviser", "reviewer", "read_only"],
        }
    )


class ConsentBody(BaseModel):
    household_id: str
    purpose: str
    granted: bool = True


@router.post("/privacy/consents")
async def add_consent(
    body: ConsentBody,
    container: Container = Depends(get_container),
    _: str = Depends(require_role("admin", "adviser", "reviewer")),
) -> dict:
    repo = IngestRepository(container.session_factory)
    consent_id = await repo.add_consent(body.household_id, body.purpose, body.granted)
    return success({"id": consent_id})


@router.get("/privacy/households/{household_id}/export")
async def export_household(
    household_id: str,
    container: Container = Depends(get_container),
    _: str = Depends(require_role("admin", "adviser")),
) -> dict:
    books = BookRepository(container.session_factory)
    desk = DeskService(books)
    queue = await desk.queue(household_id)
    consents = await IngestRepository(container.session_factory).list_consents(household_id)
    return success(
        {
            "household": queue["household"],
            "lots": queue["lots"],
            "exceptions": queue["exceptions"],
            "consents": consents,
            "maskedSample": mask_pii("PAN ABCDE1234F account 123456789012"),
        }
    )


@router.get("/metrics/desk")
async def desk_metrics(container: Container = Depends(get_container)) -> dict:
    return success(await IngestRepository(container.session_factory).metrics())


@router.post("/demo/run")
async def run_demo(container: Container = Depends(get_container)) -> dict:
    books = BookRepository(container.session_factory)
    desk = DeskService(books)
    ingest = IngestService(books, desk, IngestRepository(container.session_factory))
    await desk.ensure_seeded()
    before = await desk.queue("hh_mehta")
    form16 = ingest.parse({"household_id": "hh_mehta", "kind": "form16"})
    form16_result = await ingest.apply("hh_mehta", form16)
    bonus = ingest.parse(
        {
            "household_id": "hh_mehta",
            "kind": "text_event",
            "raw_text": "Add a 12 lakh bonus on 12 Sep 2026",
        }
    )
    bonus_result = await ingest.apply("hh_mehta", bonus)
    after = bonus_result.get("queue") or await desk.queue("hh_mehta")
    script = queue_script(after.get("exceptions") or [])
    return success(
        {
            "fixture": FORM16_FIXTURE,
            "beforeCount": len(before["exceptions"]),
            "form16": form16_result.get("status"),
            "bonus": bonus_result.get("status"),
            "afterCount": len(after.get("exceptions") or []),
            "speech": script,
            "queue": after,
            "steps": [
                "Open desk on Karan Mehta.",
                "Drop the Form 16 fixture. Extracted basic salary is grounded.",
                "Dictate a 12 lakh bonus. The book updates. Calculators re-run.",
                "Hear the top three exceptions. Same rupees as the queue.",
                "Paper trading stays off unless TRADING_CHAT_ENABLED is true.",
            ],
        }
    )
