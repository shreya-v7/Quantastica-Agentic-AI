"""Phase 3 speech: mock STT/TTS, lakh events, queue script uses given rupees."""

from __future__ import annotations

from app.speech.provider import MockSpeech, classify_utterance, queue_script


def test_mock_transcribe_text_prefix():
    speech = MockSpeech()
    assert speech.transcribe("text:What fired for Mehta") == "What fired for Mehta"


def test_query_intent_and_tts_uses_queue_rupees():
    classified = classify_utterance("What fired for Mehta")
    assert classified["intent"] == "query"
    script = queue_script(
        [
            {"title": "Reliance over name cap", "rupeeDelta": 8527250, "dueDate": None},
            {"title": "TCS lot clock", "rupeeDelta": 135625, "dueDate": "2026-10-21"},
        ]
    )
    assert "8527250" in script.replace(",", "")
    assert "135625" in script.replace(",", "")
    audio = MockSpeech().speak(script)
    assert audio.startswith("mock-audio:")
    assert "8527250" in audio.replace(",", "")


def test_bonus_event_lakh_and_confirm():
    classified = classify_utterance("Add a 12 lakh bonus on 12 Sep")
    assert classified["intent"] == "event"
    assert classified["needsConfirm"] is True
    assert classified["event"]["amount_inr"] == 1_200_000


def test_why_is_query():
    assert classify_utterance("Why is the Reliance row there")["intent"] == "query"
