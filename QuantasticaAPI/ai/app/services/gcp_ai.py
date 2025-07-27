import os
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from google.cloud import speech_v1p1beta1 as speech
from google.oauth2 import service_account

vertexai.init(project=os.getenv("GCP_PROJECT"), location=os.getenv("GCP_REGION"))

model = GenerativeModel("gemini-pro")

creds = service_account.Credentials.from_service_account_file(
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
)

speech_client = speech.SpeechClient(credentials=creds)

def gemini_prompt(prompt):
    response = model.generate_content(prompt)
    return response.text

def transcribe_audio(audio_blob):
    audio = speech.RecognitionAudio(content=audio_blob)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US"
    )
    response = speech_client.recognize(config=config, audio=audio)
    return response.results[0].alternatives[0].transcript if response.results else "