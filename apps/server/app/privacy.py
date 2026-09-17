"""PII masking for logs and LLM prompts (DPDP)."""

from __future__ import annotations

import re

PAN_RE = re.compile(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b")
ACCOUNT_RE = re.compile(r"\b(\d{9,18})\b")


def mask_pii(text: str) -> str:
    text = PAN_RE.sub(lambda m: m.group(1)[:5] + "****" + m.group(1)[-1], text)
    text = ACCOUNT_RE.sub(lambda m: m.group(1)[:2] + "****" + m.group(1)[-2:], text)
    return text
