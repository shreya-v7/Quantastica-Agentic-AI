"""JWT minting and verification for the optional auth layer."""

from __future__ import annotations

import time
from typing import Any

import jwt

from app.core.config import Settings
from app.core.errors import AuthRequiredError, ConfigError


def _secret(settings: Settings) -> str:
    if not settings.jwt_secret:
        raise ConfigError("JWT_SECRET is required when auth is enabled")
    return settings.jwt_secret


def mint_token(settings: Settings, subject: str, ttl_seconds: int = 3600) -> str:
    now = int(time.time())
    payload = {"sub": subject, "iat": now, "exp": now + ttl_seconds}
    return jwt.encode(payload, _secret(settings), algorithm=settings.jwt_algorithm)


def verify_token(settings: Settings, token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, _secret(settings), algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise AuthRequiredError("Invalid or expired token") from exc
