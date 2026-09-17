"""Indian finance news via NewsAPI, restricted to Indian sources."""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod

import httpx
from pydantic import BaseModel

from app.core.errors import ProviderUnavailableError

INDIAN_DOMAINS = (
    "economictimes.indiatimes.com,livemint.com,moneycontrol.com,business-standard.com"
)


class NewsItem(BaseModel):
    id: str
    title: str
    url: str
    source: str
    published_at: str
    description: str = ""


class NewsProvider(ABC):
    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> list[NewsItem]: ...


class NewsApiIndia(NewsProvider):
    def __init__(self, api_key: str, timeout_seconds: float = 10.0):
        self._api_key = api_key
        self._timeout = timeout_seconds

    async def search(self, query: str, limit: int = 10) -> list[NewsItem]:
        params = {
            "q": query,
            "domains": INDIAN_DOMAINS,
            "sortBy": "publishedAt",
            "pageSize": limit,
            "apiKey": self._api_key,
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get("https://newsapi.org/v2/everything", params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError("news", str(exc)) from exc
        items = []
        for article in payload.get("articles", []):
            url = article.get("url", "")
            items.append(
                NewsItem(
                    id=hashlib.sha256(url.encode()).hexdigest()[:16],
                    title=article.get("title", ""),
                    url=url,
                    source=(article.get("source") or {}).get("name", ""),
                    published_at=article.get("publishedAt", ""),
                    description=article.get("description") or "",
                )
            )
        return items
