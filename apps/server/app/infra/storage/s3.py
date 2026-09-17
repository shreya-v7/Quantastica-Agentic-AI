"""S3-compatible blob storage. Serves MinIO locally (S3_ENDPOINT_URL) and AWS S3."""

from __future__ import annotations

import asyncio

import boto3

from app.infra.storage.base import BlobStorage


class S3Storage(BlobStorage):
    def __init__(
        self,
        bucket: str,
        region: str | None = None,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
    ):
        self._client = boto3.client(
            "s3",
            region_name=region,
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        self._bucket = bucket
        self._endpoint = endpoint_url

    async def put(self, key: str, data: bytes, content_type: str) -> str:
        await asyncio.to_thread(
            self._client.put_object,
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return f"s3://{self._bucket}/{key}"

    async def get(self, key: str) -> bytes:
        response = await asyncio.to_thread(
            self._client.get_object, Bucket=self._bucket, Key=key
        )
        return response["Body"].read()
