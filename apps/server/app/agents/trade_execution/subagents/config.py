"""Trade execution configuration - credentials loaded from centralized config."""

from app.config import settings

API_KEY = settings.alpaca_api_key
SECRET_KEY = settings.alpaca_secret_key
