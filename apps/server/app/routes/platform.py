from fastapi import APIRouter, Depends

from app.core.dependencies import get_container
from app.core.envelope import success
from app.infra.factory import Container

router = APIRouter()


@router.get("/platform")
def platform(container: Container = Depends(get_container)) -> dict:
    return success(container.status())
