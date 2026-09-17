"""Automation rule endpoints (Phase F). Rules are bounded by server hard caps and only
fire when the account-level automation master switch is on."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.dependencies import current_user_id, get_container, rate_limit
from app.core.envelope import success
from app.infra.factory import Container
from app.infra.repo.auth_repo import AuthRepository
from app.infra.repo.automation_repo import AutomationRepository
from app.schemas.automation import CreateAutomationRule
from app.services.automation_service import AutomationService

router = APIRouter(prefix="/automation")


def _service(container: Container) -> AutomationService:
    return AutomationService(
        AutomationRepository(container.session_factory),
        AuthRepository(container.session_factory),
        container.settings,
    )


class Toggle(BaseModel):
    enabled: bool


@router.post("/rules", dependencies=[Depends(rate_limit("automation", "money"))])
async def create_rule(
    body: CreateAutomationRule,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return success(await _service(container).create_rule(user_id, body))


@router.get("/rules")
async def list_rules(
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    return success(await _service(container).list_rules(user_id))


@router.post("/rules/{rule_id}/toggle")
async def toggle_rule(
    rule_id: str,
    body: Toggle,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    await _service(container).set_enabled(user_id, rule_id, body.enabled)
    return success({"ruleId": rule_id, "enabled": body.enabled})


@router.delete("/rules/{rule_id}")
async def delete_rule(
    rule_id: str,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    await _service(container).delete_rule(user_id, rule_id)
    return success({"ruleId": rule_id, "deleted": True})


@router.post("/master")
async def master_toggle(
    body: Toggle,
    user_id: str = Depends(current_user_id),
    container: Container = Depends(get_container),
) -> dict:
    await _service(container).set_automation_enabled(user_id, body.enabled)
    return success({"automationEnabled": body.enabled})
