"""Speech providers. Sarvam/Transcribe are adapters; tests use MockSpeech."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ingest.extractors import parse_text_event


class SpeechProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_b64: str, language: str = "en-IN") -> str: ...

    @abstractmethod
    def speak(self, text: str, language: str = "en-IN") -> str: ...


class MockSpeech(SpeechProvider):
    def transcribe(self, audio_b64: str, language: str = "en-IN") -> str:
        if audio_b64.startswith("text:"):
            return audio_b64[5:]
        return "What fired for Mehta"

    def speak(self, text: str, language: str = "en-IN") -> str:
        return f"mock-audio:{text[:80]}"


def timed_speak(provider: SpeechProvider, text: str, language: str = "en-IN") -> dict:
    from time import perf_counter

    start = perf_counter()
    audio = provider.speak(text, language)
    elapsed = (perf_counter() - start) * 1000
    return {"audio": audio, "ttfa_ms": elapsed, "e2e_ms": elapsed, "budget_ms": 1500}


def classify_utterance(transcript: str) -> dict:
    lower = transcript.lower()
    if "why" in lower or "fired" in lower or "what" in lower:
        intent = "query"
    elif "buy" in lower or "sell" in lower:
        intent = "trade"
    else:
        intent = "event"
    event = parse_text_event(transcript)
    return {
        "transcript": transcript,
        "intent": intent,
        "event": event.model_dump(mode="json"),
        "needsConfirm": event.event_type == "bonus" and event.amount_inr is not None,
    }


def queue_script(exceptions: list[dict]) -> str:
    lines = []
    for row in exceptions[:3]:
        title = str(row.get("title") or row.get("ruleId") or "exception")
        rupee = row.get("rupeeDelta") or row.get("rupee_delta") or 0
        due = row.get("dueDate") or row.get("due_date") or ""
        lines.append(f"{title}. Rs {rupee:,.0f}. {due}".strip())
    if not lines:
        return "No open exceptions."
    return " ".join(lines)
