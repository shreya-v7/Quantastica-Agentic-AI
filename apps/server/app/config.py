"""
Centralized configuration for Quantastica API.

ALL credentials live in a single .env file -- no separate JSON key files.
Import `settings` from this module everywhere.
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional
from google.oauth2 import service_account


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # --- Google Cloud / Firebase Service Account ---
    gcp_project: str = ""
    gcp_region: str = "us-central1"
    gcp_service_account_email: str = ""
    gcp_private_key: str = ""
    gcp_private_key_id: str = ""
    gcp_client_id: str = ""

    # --- Server ---
    base_url: str = "http://localhost:8000"
    agent_mode: str = "in_process"

    # --- Alpaca Trading ---
    alpaca_api_key: str = ""
    alpaca_secret_key: str = ""

    # --- Twilio ---
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_whatsapp: str = "whatsapp:+14155238886"
    twilio_to_whatsapp: str = "whatsapp:+918451920618"

    # --- NewsAPI ---
    newsapi_key: str = ""

    # --- Test Data ---
    test_data_dir: Optional[str] = None

    @property
    def resolved_test_data_dir(self) -> str:
        if self.test_data_dir:
            return self.test_data_dir
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_data_dir")

    @property
    def service_account_info(self) -> dict:
        """Build the service-account dict that Firebase/GCP SDKs expect."""
        return {
            "type": "service_account",
            "project_id": self.gcp_project,
            "private_key_id": self.gcp_private_key_id,
            "private_key": self.gcp_private_key.replace("\\n", "\n"),
            "client_email": self.gcp_service_account_email,
            "client_id": self.gcp_client_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "universe_domain": "googleapis.com",
        }

    def get_gcp_credentials(self, scopes: Optional[list] = None):
        """Build google.oauth2 Credentials from .env fields."""
        creds = service_account.Credentials.from_service_account_info(
            self.service_account_info
        )
        if scopes:
            creds = creds.with_scopes(scopes)
        return creds

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
