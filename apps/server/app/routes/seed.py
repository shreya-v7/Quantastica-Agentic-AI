from fastapi import APIRouter, Depends

from app.core.config import Settings
from app.core.dependencies import get_container, get_settings
from app.core.envelope import success
from app.core.errors import ForbiddenError
from app.infra.factory import Container
from app.seed import loader

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
    return success(await loader.load_into(container.repository))


@router.post("/reset")
async def reset_seed(
    settings: Settings = Depends(get_settings),
    container: Container = Depends(get_container),
) -> dict:
    _guard(settings)
    return success(await loader.reset(container.repository))
