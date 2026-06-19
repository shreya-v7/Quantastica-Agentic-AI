"""Trade endpoints (Phase F). Creating an intent is rate-limited; executing one requires
fresh authentication (recent sign-in) on top of the standard auth."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.dependencies import (
    current_user_id,
    get_container,
    rate_limit,
    require_fresh_auth,
)
from app.core.envelope import success
from app.infra.factory import Container
from app.schemas.trade import CreateOrderIntent
from app.services.trade_service import TradeService

router = APIRouter(prefix="/trades")


def _service(container: Container) -> TradeService:
    return TradeService(container)


@router.post("/intents", dependencies=[Depends(rate_limit("trade", "money"))])
async def create_intent(
    body: CreateOrderIntent,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return success(await _service(container).create_intent(user_id, body))


@router.get("/intents")
async def list_intents(
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return success(await _service(container).list_intents(user_id))


@router.get("/intents/{intent_id}")
async def get_intent(
    intent_id: str,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return success(await _service(container).get_intent(user_id, intent_id))


@router.post(
    "/intents/{intent_id}/execute",
    dependencies=[Depends(rate_limit("trade", "money"))],
)
async def execute_intent(
    intent_id: str,
    user_id: str = Depends(require_fresh_auth),
    container: Container = Depends(get_container),
) -> dict:
    return success(await _service(container).approve_and_execute(user_id, intent_id))


@router.post("/intents/{intent_id}/cancel")
async def cancel_intent(
    intent_id: str,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return success(await _service(container).cancel_intent(user_id, intent_id))


class KillSwitch(BaseModel):
    disabled: bool


@router.post("/kill-switch")
async def kill_switch(
    body: KillSwitch,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    await _service(container).set_kill_switch(user_id, body.disabled)
    return success({"tradingDisabled": body.disabled})
