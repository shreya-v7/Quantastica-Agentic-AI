from typing import Literal

from pydantic import Field

from app.schemas.base import Contract
from app.schemas.common import AlertOperator

AlertKind = Literal["price", "percent_move", "sentiment_flip"]


class CreateAlert(Contract):
    name: str = Field(min_length=1, max_length=128)
    # `price`: cross `threshold` per `operator`.
    # `percent_move`: absolute day move >= `threshold` (fraction, e.g. 0.05 = 5%).
    # `sentiment_flip`: agent sentiment label changes from the last observation.
    kind: AlertKind = "price"
    symbol: str = Field(min_length=1)
    operator: AlertOperator = "above"
    threshold: float = Field(default=0.0, ge=0)
    channel: str = Field(default="whatsapp")
    cooldown_seconds: int = Field(default=3600, ge=60)


class Alert(Contract):
    id: str
    name: str
    kind: AlertKind
    symbol: str
    operator: AlertOperator
    threshold: float
    channel: str
    enabled: bool
    cooldown_seconds: int
    last_label: str | None
    last_triggered_at: str | None
    created_at: str
