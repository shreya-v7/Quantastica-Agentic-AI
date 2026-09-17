"""Broker interface. Paper engine is the default everywhere; Kite Connect is the
prod-gated live implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel


class BrokerOrder(BaseModel):
    symbol: str
    side: Literal["buy", "sell"]
    quantity: float
    order_type: Literal["market", "limit"]
    limit_price: float | None = None


class BrokerResult(BaseModel):
    status: Literal["filled", "rejected"]
    fill_price: float | None = None
    broker_order_id: str
    reason: str | None = None


class Broker(ABC):
    @abstractmethod
    async def place_order(self, order: BrokerOrder) -> BrokerResult: ...
