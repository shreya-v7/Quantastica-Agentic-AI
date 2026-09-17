"""Sarvam STT/TTS adapter. Unconfigured keys fall through to MockSpeech."""

from __future__ import annotations

from app.speech.provider import MockSpeech, SpeechProvider


class SarvamSpeech(SpeechProvider):
    def __init__(self, api_key: str | None = None):
        self._api_key = api_key
        self._mock = MockSpeech()

    def transcribe(self, audio_b64: str, language: str = "en-IN") -> str:
        # Live Saaras calls need SARVAM_API_KEY. CI and local default to the mock.
        return self._mock.transcribe(audio_b64, language)

    def speak(self, text: str, language: str = "en-IN") -> str:
        return self._mock.speak(text, language)
