"""Price alert endpoints (Phase G)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.dependencies import current_user_id, get_container
from app.core.envelope import success
from app.infra.factory import Container
from app.infra.repo.alert_repo import AlertRepository
from app.providers.marketdata.base import validate_symbol
from app.schemas.alert import CreateAlert

router = APIRouter(prefix="/alerts")


class Toggle(BaseModel):
    enabled: bool


@router.post("")
async def create_alert(
    body: CreateAlert,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    body = body.model_copy(update={"symbol": validate_symbol(body.symbol)})
    return success(await AlertRepository(container.session_factory).create(user_id, body))


@router.get("")
async def list_alerts(
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return success(await AlertRepository(container.session_factory).list(user_id))


@router.post("/{alert_id}/toggle")
async def toggle_alert(
    alert_id: str,
    body: Toggle,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    await AlertRepository(container.session_factory).set_enabled(user_id, alert_id, body.enabled)
    return success({"alertId": alert_id, "enabled": body.enabled})


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: str,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    await AlertRepository(container.session_factory).delete(user_id, alert_id)
    return success({"alertId": alert_id, "deleted": True})
