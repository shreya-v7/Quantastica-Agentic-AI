"""Authentication service: registration, login with lockout and TOTP, refresh-token
rotation with reuse detection, and TOTP enrollment. Every outcome is audited."""

from __future__ import annotations

from datetime import UTC, datetime

import pyotp

from app.core.config import Settings
from app.core.errors import AuthRequiredError, ForbiddenError, ValidationError
from app.core.ids import new_id
from app.core.passwords import hash_password, needs_rehash, verify_password
from app.core.security import (
    hash_token,
    mint_access_token,
    new_refresh_token,
)
from app.infra.db.models import UserRow
from app.infra.repo.auth_repo import AuthRepository
from app.schemas.auth import TokenPair, TotpSetup, UserProfile

TOTP_ISSUER = "Quantastica"


class AuthService:
    def __init__(self, repo: AuthRepository, settings: Settings):
        self._repo = repo
        self._settings = settings

    async def register(self, email: str, password: str, ip: str | None) -> UserProfile:
        existing = await self._repo.get_user_by_email(email)
        if existing is not None:
            # Do not reveal which emails exist; the message is generic.
            raise ValidationError("Unable to register with the provided details.")
        user = await self._repo.create_user(new_id("usr"), email, hash_password(password))
        await self._repo.audit(user.id, "auth.register", {"email": email}, ip)
        return _profile(user)

    async def login(
        self, email: str, password: str, totp_code: str | None, ip: str | None
    ) -> TokenPair:
        user = await self._repo.get_user_by_email(email)
        if user is None or not user.password_hash:
            raise AuthRequiredError("Invalid credentials")

        if user.locked_until and user.locked_until > datetime.now(UTC):
            await self._repo.audit(user.id, "auth.login_locked", {}, ip)
            raise ForbiddenError("Account temporarily locked. Try again later.")

        if not verify_password(user.password_hash, password):
            await self._repo.record_login_failure(
                user.id, self._settings.login_max_attempts, self._settings.login_lock_minutes
            )
            await self._repo.audit(user.id, "auth.login_failed", {}, ip)
            raise AuthRequiredError("Invalid credentials")

        if user.totp_enabled:
            if not totp_code:
                raise AuthRequiredError("TOTP code required")
            if not pyotp.TOTP(user.totp_secret).verify(totp_code, valid_window=1):
                await self._repo.record_login_failure(
                    user.id, self._settings.login_max_attempts, self._settings.login_lock_minutes
                )
                await self._repo.audit(user.id, "auth.totp_failed", {}, ip)
                raise AuthRequiredError("Invalid TOTP code")

        if needs_rehash(user.password_hash):
            await self._repo.update_password_hash(user.id, hash_password(password))
        await self._repo.record_login_success(user.id)
        await self._repo.audit(user.id, "auth.login", {}, ip)
        return await self._issue_pair(user.id, user.role, family_id=new_id("fam"))

    async def refresh(self, refresh_token: str, ip: str | None) -> TokenPair:
        token_hash = hash_token(refresh_token)
        row = await self._repo.get_refresh(token_hash)
        if row is None:
            raise AuthRequiredError("Invalid refresh token")
        if row.revoked:
            # Reuse of a rotated/revoked token: treat the whole family as compromised.
            await self._repo.revoke_family(row.family_id)
            await self._repo.audit(row.user_id, "auth.refresh_reuse", {"family": row.family_id}, ip)
            raise AuthRequiredError("Refresh token reuse detected. Please sign in again.")
        if row.expires_at <= datetime.now(UTC):
            raise AuthRequiredError("Refresh token expired")

        user = await self._repo.get_user(row.user_id)
        if user is None:
            raise AuthRequiredError("Invalid refresh token")
        new_plain = new_refresh_token()
        await self._repo.rotate_refresh(
            row, hash_token(new_plain), self._settings.refresh_token_ttl_seconds
        )
        await self._repo.audit(user.id, "auth.refresh", {}, ip)
        access = mint_access_token(self._settings, user.id, user.role)
        return TokenPair(
            access_token=access,
            refresh_token=new_plain,
            expires_in=self._settings.access_token_ttl_seconds,
        )

    async def start_totp(self, user_id: str) -> TotpSetup:
        user = await self._repo.get_user(user_id)
        if user is None:
            raise AuthRequiredError("Unknown user")
        secret = pyotp.random_base32()
        await self._repo.set_totp_secret(user_id, secret)
        url = pyotp.TOTP(secret).provisioning_uri(
            name=user.email or user_id, issuer_name=TOTP_ISSUER
        )
        return TotpSetup(secret=secret, otpauth_url=url)

    async def confirm_totp(self, user_id: str, code: str) -> None:
        user = await self._repo.get_user(user_id)
        if user is None or not user.totp_secret:
            raise ValidationError("Start TOTP setup before confirming.")
        if not pyotp.TOTP(user.totp_secret).verify(code, valid_window=1):
            raise ValidationError("Invalid TOTP code")
        await self._repo.enable_totp(user_id)
        await self._repo.audit(user_id, "auth.totp_enabled", {})

    async def profile(self, user_id: str) -> UserProfile:
        user = await self._repo.get_user(user_id)
        if user is None:
            raise AuthRequiredError("Unknown user")
        return _profile(user)

    async def _issue_pair(self, user_id: str, role: str, family_id: str) -> TokenPair:
        plain = new_refresh_token()
        await self._repo.store_refresh(
            user_id, family_id, hash_token(plain), self._settings.refresh_token_ttl_seconds
        )
        access = mint_access_token(self._settings, user_id, role)
        return TokenPair(
            access_token=access,
            refresh_token=plain,
            expires_in=self._settings.access_token_ttl_seconds,
        )


def _profile(user: UserRow) -> UserProfile:
    return UserProfile(
        id=user.id,
        email=user.email,
        role=user.role,
        totp_enabled=user.totp_enabled,
        automation_enabled=user.automation_enabled,
        trading_disabled=user.trading_disabled,
    )
