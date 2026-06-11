"""Mutual fund NAV provider interface. AMFI scheme code is the key everywhere."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel


class NavPoint(BaseModel):
    date: str
    nav: float


class SchemeNav(BaseModel):
    scheme_code: str
    scheme_name: str
    nav: float
    date: str


class MfDataProvider(ABC):
    @abstractmethod
    async def latest_nav(self, scheme_code: str) -> SchemeNav: ...

    @abstractmethod
    async def nav_history(
        self, scheme_code: str, from_date: str, to_date: str
    ) -> list[NavPoint]: ...
