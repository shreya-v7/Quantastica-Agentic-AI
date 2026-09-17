"""Auth-related persistence: users, refresh-token rotation, and the audit trail.

Shares the same async session factory as the main repository. Token rotation and family
revocation are done in single transactions so reuse detection cannot race.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.ids import new_id
from app.infra.db.models import AuditLogRow, RefreshTokenRow, UserRow


class AuthRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._sessions = session_factory

    async def get_user_by_email(self, email: str) -> UserRow | None:
        async with self._sessions() as session:
            return await session.scalar(select(UserRow).where(UserRow.email == email))

    async def get_user(self, user_id: str) -> UserRow | None:
        async with self._sessions() as session:
            return await session.get(UserRow, user_id)

    async def get_user_by_phone(self, phone: str) -> UserRow | None:
        async with self._sessions() as session:
            return await session.scalar(select(UserRow).where(UserRow.phone == phone))

    async def create_user(self, user_id: str, email: str, password_hash: str) -> UserRow:
        async with self._sessions() as session:
            row = UserRow(
                id=user_id,
                email=email,
                password_hash=password_hash,
                role="user",
                created_at=datetime.now(UTC),
            )
            session.add(row)
            await session.commit()
            await session.refresh(row)
            return row

    async def record_login_success(self, user_id: str) -> None:
        async with self._sessions() as session:
            await session.execute(
                update(UserRow)
                .where(UserRow.id == user_id)
                .values(failed_login_count=0, locked_until=None, last_login_at=datetime.now(UTC))
            )
            await session.commit()

    async def record_login_failure(
        self, user_id: str, max_attempts: int, lock_minutes: int
    ) -> None:
        async with self._sessions() as session:
            user = await session.get(UserRow, user_id)
            if user is None:
                return
            user.failed_login_count += 1
            if user.failed_login_count >= max_attempts:
                user.locked_until = datetime.now(UTC) + timedelta(minutes=lock_minutes)
                user.failed_login_count = 0
            await session.commit()

    async def update_password_hash(self, user_id: str, password_hash: str) -> None:
        async with self._sessions() as session:
            await session.execute(
                update(UserRow).where(UserRow.id == user_id).values(password_hash=password_hash)
            )
            await session.commit()

    async def set_totp_secret(self, user_id: str, secret: str) -> None:
        async with self._sessions() as session:
            await session.execute(
                update(UserRow).where(UserRow.id == user_id).values(totp_secret=secret)
            )
            await session.commit()

    async def enable_totp(self, user_id: str) -> None:
        async with self._sessions() as session:
            await session.execute(
                update(UserRow).where(UserRow.id == user_id).values(totp_enabled=True)
            )
            await session.commit()

    async def set_trading_disabled(self, user_id: str, disabled: bool) -> None:
        async with self._sessions() as session:
            await session.execute(
                update(UserRow).where(UserRow.id == user_id).values(trading_disabled=disabled)
            )
            await session.commit()

    # --- refresh tokens -----------------------------------------------------
    async def store_refresh(
        self, user_id: str, family_id: str, token_hash: str, ttl_seconds: int
    ) -> str:
        token_id = new_id("rt")
        async with self._sessions() as session:
            session.add(
                RefreshTokenRow(
                    id=token_id,
                    user_id=user_id,
                    family_id=family_id,
                    token_hash=token_hash,
                    expires_at=datetime.now(UTC) + timedelta(seconds=ttl_seconds),
                    created_at=datetime.now(UTC),
                )
            )
            await session.commit()
        return token_id

    async def get_refresh(self, token_hash: str) -> RefreshTokenRow | None:
        async with self._sessions() as session:
            return await session.scalar(
                select(RefreshTokenRow).where(RefreshTokenRow.token_hash == token_hash)
            )

    async def rotate_refresh(
        self, old: RefreshTokenRow, new_hash: str, ttl_seconds: int
    ) -> None:
        new_token_id = new_id("rt")
        async with self._sessions() as session:
            session.add(
                RefreshTokenRow(
                    id=new_token_id,
                    user_id=old.user_id,
                    family_id=old.family_id,
                    token_hash=new_hash,
                    expires_at=datetime.now(UTC) + timedelta(seconds=ttl_seconds),
                    created_at=datetime.now(UTC),
                )
            )
            await session.execute(
                update(RefreshTokenRow)
                .where(RefreshTokenRow.id == old.id)
                .values(revoked=True, replaced_by=new_token_id)
            )
            await session.commit()

    async def revoke_family(self, family_id: str) -> None:
        async with self._sessions() as session:
            await session.execute(
                update(RefreshTokenRow)
                .where(RefreshTokenRow.family_id == family_id)
                .values(revoked=True)
            )
            await session.commit()

    # --- admin --------------------------------------------------------------
    async def list_users(self, limit: int = 100) -> list[UserRow]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(UserRow).order_by(UserRow.created_at.desc()).limit(limit)
                )
            ).all()
        return list(rows)

    async def list_audit(self, limit: int = 100) -> list[AuditLogRow]:
        async with self._sessions() as session:
            rows = (
                await session.scalars(
                    select(AuditLogRow).order_by(AuditLogRow.created_at.desc()).limit(limit)
                )
            ).all()
        return list(rows)

    async def set_role(self, user_id: str, role: str) -> None:
        async with self._sessions() as session:
            await session.execute(update(UserRow).where(UserRow.id == user_id).values(role=role))
            await session.commit()

    # --- audit --------------------------------------------------------------
    async def audit(
        self, user_id: str | None, action: str, detail: dict, ip: str | None = None
    ) -> None:
        async with self._sessions() as session:
            session.add(
                AuditLogRow(
                    id=new_id("aud"),
                    user_id=user_id,
                    action=action,
                    detail=detail,
                    ip=ip,
                    created_at=datetime.now(UTC),
                )
            )
            await session.commit()
