from fastapi import APIRouter, Depends

from app.core.config import Settings
from app.core.dependencies import get_container, get_settings
from app.core.envelope import success
from app.core.errors import ForbiddenError
from app.infra.factory import Container
from app.infra.repo.book_repo import BookRepository
from app.seed import loader
from app.services.desk_service import DeskService

router = APIRouter(prefix="/seed")


def _guard(settings: Settings) -> None:
    if not settings.seed_enabled:
        raise ForbiddenError("Seed endpoints are disabled. Set ALLOW_SEED=true to enable.")


@router.post("/load")
async def load_seed(
    settings: Settings = Depends(get_settings),
    container: Container = Depends(get_container),
) -> dict:
    _guard(settings)
    counts = await loader.load_into(container.repository)
    books = BookRepository(container.session_factory)
    counts.update(await books.seed_demo())
    desk = DeskService(books)
    for row in await books.list_households():
        await desk.recompute(row["id"])
    return success(counts)


@router.post("/reset")
async def reset_seed(
    settings: Settings = Depends(get_settings),
    container: Container = Depends(get_container),
) -> dict:
    _guard(settings)
    return success(await loader.reset(container.repository))
