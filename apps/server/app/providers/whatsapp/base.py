"""WhatsApp channel interface. Meta Cloud API in prod, logged echo channel in dev."""

from __future__ import annotations

from abc import ABC, abstractmethod


class WhatsAppChannel(ABC):
    @abstractmethod
    async def send(self, to_e164: str, text: str) -> str:
        """Send a message, returning the provider message id."""
