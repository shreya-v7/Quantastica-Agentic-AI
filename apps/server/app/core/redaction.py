"""Log redaction (Phase M). Secrets must never reach logs: bearer/JWT tokens, phone
numbers, and long account-number-like digit runs are masked before any handler writes a
record. Applied centrally in the log formatters so every logger is covered."""

from __future__ import annotations

import re

_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Bearer tokens and bare JWTs (header.payload.signature).
    (re.compile(r"Bearer\s+[A-Za-z0-9._\-]+", re.IGNORECASE), "Bearer [REDACTED]"),
    (re.compile(r"\beyJ[A-Za-z0-9._\-]{10,}"), "[REDACTED_TOKEN]"),
    # token / secret / password key=value pairs in any quoting style.
    (
        re.compile(
            r"((?:access|refresh)?_?(?:token|secret|password|api[_-]?key)\b\"?\s*[=:]\s*\"?)"
            r"[^\s\",}]+",
            re.IGNORECASE,
        ),
        r"\1[REDACTED]",
    ),
    # Indian phone numbers (+91XXXXXXXXXX or bare 10-digit mobile starting 6-9).
    (re.compile(r"\+91[\s-]?\d{10}\b"), "+91[REDACTED]"),
    (re.compile(r"\b[6-9]\d{9}\b"), "[REDACTED_PHONE]"),
    # Account-number-like digit runs (11+ digits).
    (re.compile(r"\b\d{11,}\b"), "[REDACTED_ACCT]"),
]


def redact(text: str) -> str:
    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text
