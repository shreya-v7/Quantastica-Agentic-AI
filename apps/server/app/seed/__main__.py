"""Explicit seed loader CLI: `python -m app.seed [load|reset]`."""

from __future__ import annotations

import asyncio
import sys

from app.core.config import get_settings
from app.infra.factory import build_container
from app.infra.repo.book_repo import BookRepository
from app.seed import loader
from app.services.desk_service import DeskService


async def _run(action: str) -> dict[str, int]:
    container = build_container(get_settings())
    repository = container.repository
    books = BookRepository(container.session_factory)
    if action == "reset":
        return await loader.reset(repository)
    if action == "load":
        counts = await loader.load_into(repository)
        book_counts = await books.seed_demo()
        desk = DeskService(books)
        for row in await books.list_households():
            await desk.recompute(row["id"])
        counts.update(book_counts)
        return counts
    raise SystemExit(f"Unknown action '{action}'. Use 'load' or 'reset'.")


def main() -> None:
    action = sys.argv[1] if len(sys.argv) > 1 else "load"
    counts = asyncio.run(_run(action))
    print(f"seed {action}: {counts}")


if __name__ == "__main__":
    main()
