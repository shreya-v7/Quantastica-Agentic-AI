"""Speech: STT intents, TTS of the queue. Mock in CI. Rupees come from the desk."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.dependencies import get_container
from app.core.envelope import success
from app.infra.factory import Container
from app.infra.repo.book_repo import BookRepository
from app.infra.repo.ingest_repo import IngestRepository
from app.ingest.service import IngestService
from app.services.desk_service import DeskService
from app.speech.provider import classify_utterance, queue_script
from app.speech.sarvam import SarvamSpeech
from app.trading.intents import parse_order_text

router = APIRouter(prefix="/speech")


class SpeechBody(BaseModel):
    household_id: str
    audio_b64: str = "text:What fired for Mehta"
    language: str = "en-IN"


@router.post("/transcribe")
async def transcribe(body: SpeechBody, container: Container = Depends(get_container)) -> dict:
    speech = SarvamSpeech(container.settings.sarvam_api_key)
    transcript = speech.transcribe(body.audio_b64, body.language)
    classified = classify_utterance(transcript)
    books = BookRepository(container.session_factory)
    desk = DeskService(books)
    intent = classified["intent"]

    if intent == "query":
        queue = await desk.queue(body.household_id)
        script = queue_script(queue["exceptions"])
        return success(
            {
                **classified,
                "answer": script,
                "audio": speech.speak(script, body.language),
                "exceptions": queue["exceptions"][:3],
            }
        )

    if intent == "event":
        ingest = IngestService(books, desk, IngestRepository(container.session_factory))
        state = ingest.parse(
            {
                "household_id": body.household_id,
                "kind": "text_event",
                "raw_text": transcript,
            }
        )
        if classified.get("needsConfirm") or state.get("needs_review"):
            paused = await ingest.persist_pause(f"{body.household_id}:speech", state)
            return success(
                {
                    **classified,
                    "status": "needs_review",
                    "extracted": paused.get("extracted"),
                    "missingFields": paused.get("missing_fields") or [],
                    "threadId": f"{body.household_id}:speech",
                    "answer": "Confirm the parsed event before it hits the book.",
                }
            )
        applied = await ingest.apply(body.household_id, state)
        script = queue_script((applied.get("queue") or {}).get("exceptions") or [])
        return success(
            {
                **classified,
                **applied,
                "answer": script,
                "audio": speech.speak(script, body.language),
            }
        )

    if intent == "trade":
        draft = parse_order_text(transcript)
        return success(
            {
                **classified,
                "order": draft.model_dump(by_alias=True),
                "answer": draft.clarification
                or f"{draft.side} {draft.quantity} {draft.symbol}. Confirm in paper trading.",
            }
        )

    return success({**classified, "answer": transcript})
