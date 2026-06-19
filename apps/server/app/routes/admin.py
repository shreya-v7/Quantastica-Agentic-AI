"""Admin endpoints (Phase J). Gated by the admin role; in prod the role lives on the
access-token claims, so a non-admin token is rejected before any data is read."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.dependencies import get_container, require_admin
from app.core.envelope import success
from app.infra.factory import Container
from app.infra.repo.auth_repo import AuthRepository

router = APIRouter(prefix="/admin")


@router.get("/users")
async def list_users(
    _: str = Depends(require_admin),
    container: Container = Depends(get_container),
) -> dict:
    rows = await AuthRepository(container.session_factory).list_users()
    return success(
        [
            {
                "id": u.id,
                "email": u.email,
                "role": u.role,
                "totpEnabled": u.totp_enabled,
                "tradingDisabled": u.trading_disabled,
                "automationEnabled": u.automation_enabled,
                "createdAt": u.created_at.isoformat(),
            }
            for u in rows
        ]
    )


@router.get("/audit")
async def list_audit(
    _: str = Depends(require_admin),
    container: Container = Depends(get_container),
) -> dict:
    rows = await AuthRepository(container.session_factory).list_audit()
    return success(
        [
            {
                "id": a.id,
                "userId": a.user_id,
                "action": a.action,
                "detail": a.detail,
                "ip": a.ip,
                "createdAt": a.created_at.isoformat(),
            }
            for a in rows
        ]
    )
