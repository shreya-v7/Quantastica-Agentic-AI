"""Dev echo WhatsApp channel: every send is logged and kept in an inspectable buffer.
Used automatically in dev when the Meta Cloud API env vars are not configured."""

from __future__ import annotations

import logging
import uuid
from collections import deque

from app.providers.whatsapp.base import WhatsAppChannel

logger = logging.getLogger("quantastica.whatsapp")


class EchoWhatsApp(WhatsAppChannel):
    def __init__(self, max_messages: int = 500):
        self.sent: deque[dict[str, str]] = deque(maxlen=max_messages)

    async def send(self, to_e164: str, text: str) -> str:
        message_id = f"echo_{uuid.uuid4().hex[:12]}"
        self.sent.append({"id": message_id, "to": to_e164, "text": text})
        logger.info("whatsapp echo to=%s id=%s text=%s", to_e164, message_id, text)
        return message_id
