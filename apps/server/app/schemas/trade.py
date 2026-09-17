from pydantic import Field, model_validator

from app.schemas.base import Contract
from app.schemas.common import OrderSide, OrderStatus, OrderType, TradingMode


class CreateOrderIntent(Contract):
    portfolio_id: str = Field(min_length=1)
    symbol: str = Field(min_length=1)
    side: OrderSide
    quantity: float = Field(gt=0)
    order_type: OrderType = OrderType.market
    limit_price: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def _limit_needs_price(self) -> "CreateOrderIntent":
        if self.order_type == OrderType.limit and self.limit_price is None:
            raise ValueError("limit orders require a limitPrice")
        return self


class OrderIntent(Contract):
    id: str
    portfolio_id: str
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType
    limit_price: float | None
    mode: TradingMode
    status: OrderStatus
    source: str
    reason: str | None
    broker_order_id: str | None
    fill_price: float | None
    notional_inr: float
    created_at: str
    updated_at: str
