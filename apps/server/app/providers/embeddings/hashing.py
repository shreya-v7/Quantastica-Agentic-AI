"""Deterministic hashing embeddings for tests and offline RAG smoke checks.

Not a production embedding model. Token-hashed 512-d unit vectors so hybrid retrieval
can be tested without Voyage.
"""

from __future__ import annotations

import hashlib
import math

from app.providers.embeddings.voyage import EMBEDDING_DIMS, EmbeddingsProvider


class HashingEmbeddings(EmbeddingsProvider):
    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [_vector(text) for text in texts]


def _vector(text: str) -> list[float]:
    vec = [0.0] * EMBEDDING_DIMS
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "little") % EMBEDDING_DIMS
        vec[index] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]
