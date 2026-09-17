"""Account Aggregator (Sahamati AA framework) provider.

The designed future path for pulling real bank, loan, and insurance data with user
consent. The consent-artifact flow is modeled here against a configured AA gateway;
until onboarded with an AA (AA_CLIENT_ID, AA_CLIENT_SECRET, AA_BASE_URL), the platform
reports this provider as not configured and manual entry plus statement upload are the
live paths.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import httpx
from pydantic import BaseModel

from app.core.errors import ProviderUnavailableError


class ConsentArtifact(BaseModel):
    consent_id: str
    status: str
    consent_url: str | None = None


class AAProvider(ABC):
    @abstractmethod
    async def request_consent(self, phone_e164: str, fi_types: list[str]) -> ConsentArtifact: ...

    @abstractmethod
    async def consent_status(self, consent_id: str) -> ConsentArtifact: ...

    @abstractmethod
    async def fetch_fi_data(self, consent_id: str) -> dict: ...


class SahamatiAA(AAProvider):
    def __init__(self, client_id: str, client_secret: str, base_url: str):
        self._client_id = client_id
        self._client_secret = client_secret
        self._base = base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {"client_id": self._client_id, "client_secret": self._client_secret}

    async def _request(self, method: str, path: str, json: dict | None = None) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.request(
                    method, f"{self._base}{path}", json=json, headers=self._headers()
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError("aa", str(exc)) from exc

    async def request_consent(self, phone_e164: str, fi_types: list[str]) -> ConsentArtifact:
        payload = await self._request(
            "POST", "/consents", {"customer": {"id": phone_e164}, "fiTypes": fi_types}
        )
        return ConsentArtifact(
            consent_id=payload["consentId"],
            status=payload.get("status", "PENDING"),
            consent_url=payload.get("url"),
        )

    async def consent_status(self, consent_id: str) -> ConsentArtifact:
        payload = await self._request("GET", f"/consents/{consent_id}")
        return ConsentArtifact(consent_id=consent_id, status=payload.get("status", "UNKNOWN"))

    async def fetch_fi_data(self, consent_id: str) -> dict:
        return await self._request("GET", f"/fi/data/{consent_id}")
