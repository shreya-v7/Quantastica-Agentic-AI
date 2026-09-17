"""DPDP masking: PAN and account numbers never reach prompts or logs raw."""

from __future__ import annotations

from app.core.redaction import redact
from app.privacy import mask_pii


def test_mask_pan_and_account():
    out = mask_pii("PAN ABCDE1234F account 123456789012")
    assert "ABCDE1234F" not in out
    assert "123456789012" not in out
    assert "ABCDE" in out
    assert "12" in out or "****" in out


def test_redact_also_masks_pan():
    assert "ABCDE1234F" not in redact("holder ABCDE1234F filed AIS")
