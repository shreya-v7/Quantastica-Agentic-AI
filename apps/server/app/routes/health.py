from fastapi import APIRouter

from app import __version__
from app.core.envelope import success
from app.schemas.platform import HealthStatus

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return success(HealthStatus(status="ok", version=__version__))
