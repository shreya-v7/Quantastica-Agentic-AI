"""Zerodha Kite Connect live broker. Only reachable when every live-trading gate in
the trade service passes (prod, TRADING_MODE=live, configured keys, 2FA-backed setup)."""

from __future__ import annotations

import asyncio

import httpx

from app.core.errors import ProviderUnavailableError
from app.providers.broker.base import Broker, BrokerOrder, BrokerResult

_BASE = "https://api.kite.trade"


class KiteBroker(Broker):
    def __init__(self, api_key: str, api_secret: str, access_token: str):
        self._api_key = api_key
        self._api_secret = api_secret
        self._access_token = access_token

    def _headers(self) -> dict[str, str]:
        return {
            "X-Kite-Version": "3",
            "Authorization": f"token {self._api_key}:{self._access_token}",
        }

    async def place_order(self, order: BrokerOrder) -> BrokerResult:
        symbol, suffix = order.symbol.rsplit(".", 1)
        exchange = "NSE" if suffix == "NS" else "BSE"
        data = {
            "tradingsymbol": symbol,
            "exchange": exchange,
            "transaction_type": order.side.upper(),
            "quantity": str(int(order.quantity)),
            "order_type": order.order_type.upper(),
            "product": "CNC",
            "validity": "DAY",
        }
        if order.order_type == "limit" and order.limit_price is not None:
            data["price"] = str(order.limit_price)
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{_BASE}/orders/regular", headers=self._headers(), data=data
                )
                response.raise_for_status()
                order_id = response.json()["data"]["order_id"]
                fill = await self._await_fill(client, order_id)
                return fill
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError("broker_live", str(exc)) from exc

    async def _await_fill(self, client: httpx.AsyncClient, order_id: str) -> BrokerResult:
        for _ in range(10):
            response = await client.get(f"{_BASE}/orders/{order_id}", headers=self._headers())
            response.raise_for_status()
            entries = response.json().get("data", [])
            latest = entries[-1] if entries else {}
            status = latest.get("status", "")
            if status == "COMPLETE":
                return BrokerResult(
                    status="filled",
                    fill_price=float(latest.get("average_price") or 0.0),
                    broker_order_id=order_id,
                )
            if status in ("REJECTED", "CANCELLED"):
                return BrokerResult(
                    status="rejected",
                    broker_order_id=order_id,
                    reason=latest.get("status_message") or status,
                )
            await asyncio.sleep(1.0)
        return BrokerResult(
            status="rejected", broker_order_id=order_id, reason="Fill confirmation timed out"
        )
