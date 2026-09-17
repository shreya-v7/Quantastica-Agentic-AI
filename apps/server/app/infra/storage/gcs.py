"""Google Cloud Storage blob storage for the gcp platform."""

from __future__ import annotations

import asyncio

from google.cloud import storage

from app.infra.storage.base import BlobStorage


class GcsStorage(BlobStorage):
    def __init__(self, bucket: str):
        self._bucket_name = bucket
        self._client = storage.Client()
        self._bucket = self._client.bucket(bucket)

    async def put(self, key: str, data: bytes, content_type: str) -> str:
        blob = self._bucket.blob(key)
        await asyncio.to_thread(blob.upload_from_string, data, content_type=content_type)
        return f"gs://{self._bucket_name}/{key}"

    async def get(self, key: str) -> bytes:
        blob = self._bucket.blob(key)
        return await asyncio.to_thread(blob.download_as_bytes)
