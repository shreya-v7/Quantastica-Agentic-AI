"""
GCP AI services -- Vertex AI (Gemini) and Cloud Speech-to-Text.

Credentials are built from the single .env file via app.config.settings.
No separate JSON key file needed.
"""

import vertexai
from vertexai.preview.generative_models import GenerativeModel
from google.cloud import speech_v1p1beta1 as speech

from app.config import settings

# Vertex AI
vertexai.init(
    project=settings.gcp_project,
    location=settings.gcp_region,
    credentials=settings.get_gcp_credentials(),
)
model = GenerativeModel("gemini-pro")

# Speech-to-Text
speech_client = speech.SpeechClient(credentials=settings.get_gcp_credentials())


def gemini_prompt(prompt_text: str) -> str:
    """Send a prompt to Gemini and return the text response."""
    response = model.generate_content(prompt_text)
    return response.text


def transcribe_audio(audio_blob: bytes) -> str:
    """Transcribe audio bytes using Cloud Speech-to-Text."""
    audio = speech.RecognitionAudio(content=audio_blob)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
    )
    response = speech_client.recognize(config=config, audio=audio)
    if response.results:
        return response.results[0].alternatives[0].transcript
    return ""
