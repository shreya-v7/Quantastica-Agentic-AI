"""Blob storage interface for report exports and uploaded documents.

Implementations: local disk (zero-dependency dev), S3 compatible (MinIO locally via
S3_ENDPOINT_URL, AWS S3 in prod), GCS on GCP.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BlobStorage(ABC):
    @abstractmethod
    async def put(self, key: str, data: bytes, content_type: str) -> str: ...

    @abstractmethod
    async def get(self, key: str) -> bytes: ...
