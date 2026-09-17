from pydantic import Field, model_validator

from app.schemas.base import Contract
from app.schemas.common import AlertOperator, OrderSide, OrderType


class AutomationTrigger(Contract):
    symbol: str = Field(min_length=1)
    operator: AlertOperator
    price: float = Field(gt=0)


class AutomationAction(Contract):
    side: OrderSide
    quantity: float = Field(gt=0)
    order_type: OrderType = OrderType.market
    limit_price: float | None = Field(default=None, gt=0)


class CreateAutomationRule(Contract):
    name: str = Field(min_length=1, max_length=128)
    portfolio_id: str = Field(min_length=1)
    trigger: AutomationTrigger
    action: AutomationAction
    max_notional_inr: float = Field(gt=0)
    cooldown_seconds: int = Field(default=3600, ge=60)

    @model_validator(mode="after")
    def _limit_needs_price(self) -> "CreateAutomationRule":
        if self.action.order_type == OrderType.limit and self.action.limit_price is None:
            raise ValueError("limit action requires a limitPrice")
        return self


class AutomationRule(Contract):
    id: str
    name: str
    enabled: bool
    portfolio_id: str
    trigger: AutomationTrigger
    action: AutomationAction
    max_notional_inr: float
    cooldown_seconds: int
    executions_today: int
    day_notional_inr: float
    last_fired_at: str | None
    created_at: str
