"""Meta WhatsApp Cloud API channel."""

from __future__ import annotations

import httpx

from app.core.errors import ProviderUnavailableError
from app.providers.whatsapp.base import WhatsAppChannel


class MetaWhatsApp(WhatsAppChannel):
    def __init__(self, token: str, phone_id: str, timeout_seconds: float = 10.0):
        self._token = token
        self._phone_id = phone_id
        self._timeout = timeout_seconds

    async def send(self, to_e164: str, text: str) -> str:
        url = f"https://graph.facebook.com/v20.0/{self._phone_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to_e164.lstrip("+"),
            "type": "text",
            "text": {"body": text},
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    url, json=payload, headers={"Authorization": f"Bearer {self._token}"}
                )
                response.raise_for_status()
                return response.json()["messages"][0]["id"]
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError("whatsapp", str(exc)) from exc
