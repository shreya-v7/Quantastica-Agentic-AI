"""Placeholder for a second live broker. Never holds funds. Not linked in this repo."""

from __future__ import annotations

from app.core.errors import ProviderNotConfiguredError
from app.providers.broker.base import Broker, BrokerOrder, BrokerResult


class StubBroker(Broker):
    async def place_order(self, order: BrokerOrder) -> BrokerResult:
        raise ProviderNotConfiguredError("broker_stub", ["BROKER_STUB_LINK"])
