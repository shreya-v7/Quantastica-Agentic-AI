"""JWT access tokens, opaque refresh tokens, and token hashing.

Access tokens are short-lived signed JWTs carrying the subject, role, and an `fresh`
issued-at used to enforce a fresh-auth window on money-path actions. Refresh tokens are
opaque random strings; only their SHA-256 hash is stored, and rotation links each token
to its successor so reuse of a spent token is detectable.
"""

from __future__ import annotations

import hashlib
import secrets
import time
from typing import Any

import jwt

from app.core.config import Settings
from app.core.errors import AuthRequiredError, ConfigError

# In dev without a configured secret we fall back to a fixed value so the optional auth
# layer is exercisable. Prod validation forces a strong JWT_SECRET at startup.
_DEV_SECRET = "dev-insecure-jwt-secret-not-for-production-use-only"


def _secret(settings: Settings) -> str:
    if settings.jwt_secret:
        return settings.jwt_secret
    if settings.is_prod:
        raise ConfigError("JWT_SECRET is required in prod")
    return _DEV_SECRET


def mint_access_token(settings: Settings, subject: str, role: str = "user") -> str:
    now = int(time.time())
    payload = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + settings.access_token_ttl_seconds,
        "typ": "access",
    }
    return jwt.encode(payload, _secret(settings), algorithm=settings.jwt_algorithm)


# Kept for the dev session route and existing callers.
def mint_token(settings: Settings, subject: str, ttl_seconds: int | None = None) -> str:
    return mint_access_token(settings, subject)


def verify_token(settings: Settings, token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, _secret(settings), algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise AuthRequiredError("Invalid or expired token") from exc


def is_fresh(claims: dict[str, Any], window_seconds: int) -> bool:
    issued = int(claims.get("iat", 0))
    return (int(time.time()) - issued) <= window_seconds


def new_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
