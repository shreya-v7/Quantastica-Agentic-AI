"""Bank book-of-record adapter.

Production: the bank's wealth / CBS API. Local and demos: Mock Northstar Private.
The rest of Quantastica should depend on this interface, not on a named core.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BankProvider(ABC):
    @abstractmethod
    def status(self) -> dict[str, Any]: ...

    @abstractmethod
    def list_customers(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def customer(self, customer_id: str) -> dict[str, Any]: ...

    @abstractmethod
    def accounts(self, customer_id: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    def holdings(self, customer_id: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    def transactions(self, customer_id: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    def snapshot(self, customer_id: str) -> dict[str, Any]: ...
