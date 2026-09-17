"""Event publisher interface.

Redis Streams is the default transport on every platform. The in-process publisher
serves tests and zero-dependency dev. Pub/Sub or SQS can be swapped in later through
this same interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EventPublisher(ABC):
    @abstractmethod
    async def publish(self, event_type: str, payload: dict[str, Any]) -> None: ...
