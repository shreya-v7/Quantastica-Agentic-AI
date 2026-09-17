"""Phase M: log redaction must mask tokens, phone numbers, and account numbers."""

from __future__ import annotations

from app.core.redaction import redact
from app.infra.llm.anthropic import _estimate_cost_usd


def test_redacts_bearer_and_jwt():
    out = redact("auth header Bearer abc.def.ghi used")
    assert "abc.def.ghi" not in out
    assert "[REDACTED]" in out
    jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w"
    assert "eyJhbGci" not in redact(f"token {jwt}")


def test_redacts_phone_numbers():
    assert "9876543210" not in redact("call +91 9876543210 now")
    assert "9876543210" not in redact("mobile 9876543210")


def test_redacts_account_numbers():
    assert "123456789012" not in redact("account 123456789012 credited")


def test_redacts_key_value_secrets():
    out = redact('{"refreshToken": "supersecretvalue123"}')
    assert "supersecretvalue123" not in out


def test_keeps_ordinary_text():
    assert redact("portfolio value is 4 lakh") == "portfolio value is 4 lakh"


def test_llm_cost_estimate_positive():
    cost = _estimate_cost_usd("claude-3-5-haiku-20241022", 1000, 500)
    assert cost > 0
