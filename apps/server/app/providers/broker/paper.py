"""Paper trading engine. Fills against the live NSE quote from the market data
provider. Market orders fill at the quote; limit orders fill only when marketable."""

from __future__ import annotations

import uuid

from app.providers.broker.base import Broker, BrokerOrder, BrokerResult
from app.providers.marketdata.base import MarketDataProvider


class PaperBroker(Broker):
    def __init__(self, marketdata: MarketDataProvider):
        self._marketdata = marketdata

    async def place_order(self, order: BrokerOrder) -> BrokerResult:
        quote = await self._marketdata.quote(order.symbol)
        order_id = f"paper_{uuid.uuid4().hex[:12]}"
        if order.order_type == "limit" and order.limit_price is not None:
            marketable = (
                quote.price <= order.limit_price
                if order.side == "buy"
                else quote.price >= order.limit_price
            )
            if not marketable:
                return BrokerResult(
                    status="rejected",
                    broker_order_id=order_id,
                    reason=(
                        f"Limit {order.limit_price} not marketable against live quote "
                        f"{quote.price}"
                    ),
                )
            return BrokerResult(
                status="filled", fill_price=order.limit_price, broker_order_id=order_id
            )
        return BrokerResult(status="filled", fill_price=quote.price, broker_order_id=order_id)
