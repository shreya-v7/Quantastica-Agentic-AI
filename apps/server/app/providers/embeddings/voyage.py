"""Voyage AI embeddings provider for RAG (pgvector). Built only when VOYAGE_API_KEY is
set; otherwise GET /api/platform reports it not configured."""

from __future__ import annotations

from abc import ABC, abstractmethod

import httpx

from app.core.errors import ProviderUnavailableError

EMBEDDING_DIMS = 512
_MODEL = "voyage-3-lite"


class EmbeddingsProvider(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class VoyageEmbeddings(EmbeddingsProvider):
    def __init__(self, api_key: str, timeout_seconds: float = 10.0):
        self._api_key = api_key
        self._timeout = timeout_seconds

    async def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    "https://api.voyageai.com/v1/embeddings",
                    json={"model": _MODEL, "input": texts, "output_dimension": EMBEDDING_DIMS},
                    headers={"Authorization": f"Bearer {self._api_key}"},
                )
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError("embeddings", str(exc)) from exc
        return [item["embedding"] for item in payload["data"]]
