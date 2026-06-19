"""Automation service. User-defined rules are bounded by server-enforced hard caps that
the user cannot raise: per-order notional, executions per day, and daily notional. The
firing decision is a pure function so it is exhaustively testable; the worker only wires
it to live quotes and the trade service.
"""

from __future__ import annotations

from datetime import datetime

from app.core.config import Settings
from app.core.errors import ForbiddenError, NotFoundError, ValidationError
from app.infra.db.models import AutomationRuleRow
from app.infra.repo.auth_repo import AuthRepository
from app.infra.repo.automation_repo import AutomationRepository
from app.schemas.automation import AutomationRule, CreateAutomationRule
from app.schemas.common import AlertOperator


def trigger_met(operator: str, price: float, threshold: float) -> bool:
    if operator == AlertOperator.above.value:
        return price >= threshold
    return price <= threshold


def fire_decision(
    rule: AutomationRuleRow,
    price: float,
    now: datetime,
    user_automation_enabled: bool,
    settings: Settings,
) -> tuple[bool, str]:
    """Return (should_fire, reason). Reason explains a skip or a go."""
    if not user_automation_enabled:
        return False, "automation disabled for user"
    if not rule.enabled:
        return False, "rule disabled"
    if not trigger_met(rule.trigger["operator"], price, float(rule.trigger["price"])):
        return False, "trigger condition not met"
    if rule.last_fired_at is not None:
        elapsed = (now - rule.last_fired_at).total_seconds()
        if elapsed < rule.cooldown_seconds:
            return False, "within cooldown"
    today = now.date().isoformat()
    execs = rule.executions_today if rule.counter_date == today else 0
    day_notional = rule.day_notional_inr if rule.counter_date == today else 0.0
    if execs >= settings.automation_hard_max_executions_per_day:
        return False, "daily execution cap reached"
    qty = float(rule.action["quantity"])
    notional = qty * price
    if notional > settings.automation_hard_max_notional_inr:
        return False, "order notional over hard cap"
    if notional > rule.max_notional_inr:
        return False, "order notional over rule cap"
    if day_notional + notional > settings.automation_hard_max_daily_notional_inr:
        return False, "daily notional hard cap reached"
    return True, "ok"


class AutomationService:
    def __init__(self, repo: AutomationRepository, auth: AuthRepository, settings: Settings):
        self._repo = repo
        self._auth = auth
        self._settings = settings

    async def create_rule(self, user_id: str, req: CreateAutomationRule) -> AutomationRule:
        if req.max_notional_inr > self._settings.automation_hard_max_notional_inr:
            raise ValidationError(
                f"maxNotionalInr cannot exceed the platform hard cap "
                f"{self._settings.automation_hard_max_notional_inr:.0f}."
            )
        rule = await self._repo.create(user_id, req)
        await self._auth.audit(user_id, "automation.rule_created", {"ruleId": rule.id})
        return rule

    async def list_rules(self, user_id: str) -> list[AutomationRule]:
        return await self._repo.list(user_id)

    async def set_enabled(self, user_id: str, rule_id: str, enabled: bool) -> None:
        await self._repo.set_enabled(user_id, rule_id, enabled)
        await self._auth.audit(
            user_id, "automation.rule_toggled", {"ruleId": rule_id, "enabled": enabled}
        )

    async def delete_rule(self, user_id: str, rule_id: str) -> None:
        await self._repo.delete(user_id, rule_id)
        await self._auth.audit(user_id, "automation.rule_deleted", {"ruleId": rule_id})

    async def set_automation_enabled(self, user_id: str, enabled: bool) -> None:
        user = await self._auth.get_user(user_id)
        if user is None:
            raise NotFoundError("Unknown user")
        # 2FA is mandatory before automation can act on the account.
        if enabled and self._settings.auth_enabled and not user.totp_enabled:
            raise ForbiddenError("Enable 2FA (TOTP) before turning on automation.")
        async with self._repo._sessions() as session:  # noqa: SLF001
            row = await session.get(type(user), user_id)
            if row is not None:
                row.automation_enabled = enabled
                await session.commit()
        await self._auth.audit(user_id, "automation.master_toggle", {"enabled": enabled})

    async def assert_owned(self, user_id: str, rule_id: str) -> None:
        rules = await self._repo.list(user_id)
        if not any(r.id == rule_id for r in rules):
            raise ForbiddenError("Rule not found for this user")
