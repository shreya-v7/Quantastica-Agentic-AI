"""Pure security primitives: Argon2id hashing, JWT freshness, refresh-token hashing."""

from __future__ import annotations

import time

from app.core.config import Settings
from app.core.passwords import hash_password, verify_password
from app.core.security import (
    hash_token,
    is_fresh,
    mint_access_token,
    new_refresh_token,
    verify_token,
)


def _settings() -> Settings:
    return Settings(
        _env_file=None, app_env="dev", platform="local", anthropic_api_key="x",
        jwt_secret="a" * 40,
    )


def test_argon2_roundtrip():
    h = hash_password("correct horse battery staple")
    assert h.startswith("$argon2id$")
    assert verify_password(h, "correct horse battery staple")
    assert not verify_password(h, "wrong password")


def test_access_token_carries_subject_and_role():
    s = _settings()
    token = mint_access_token(s, "usr_1", "admin")
    claims = verify_token(s, token)
    assert claims["sub"] == "usr_1"
    assert claims["role"] == "admin"
    assert claims["typ"] == "access"


def test_is_fresh_window():
    now = int(time.time())
    assert is_fresh({"iat": now}, 300) is True
    assert is_fresh({"iat": now - 600}, 300) is False


def test_refresh_token_hash_is_stable_and_opaque():
    plain = new_refresh_token()
    assert len(plain) > 40
    assert hash_token(plain) == hash_token(plain)
    assert hash_token(plain) != plain
