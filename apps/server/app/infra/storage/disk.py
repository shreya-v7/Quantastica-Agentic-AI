"""Local disk blob storage for zero-dependency dev."""

from __future__ import annotations

import asyncio
from pathlib import Path

from app.infra.storage.base import BlobStorage


class DiskStorage(BlobStorage):
    def __init__(self, base_dir: str):
        self._base = Path(base_dir)
        self._base.mkdir(parents=True, exist_ok=True)

    async def put(self, key: str, data: bytes, content_type: str) -> str:
        target = self._base / key
        target.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(target.write_bytes, data)
        return str(target.resolve())

    async def get(self, key: str) -> bytes:
        return await asyncio.to_thread((self._base / key).read_bytes)
