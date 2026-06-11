from fastapi import APIRouter, Depends, Query

from app.core.dependencies import current_user_id, insight_service
from app.core.envelope import success
from app.schemas.common import Severity
from app.services.insight_service import InsightService

router = APIRouter(prefix="/insights")


@router.get("")
async def list_insights(
    portfolio_id: str | None = Query(default=None, alias="portfolioId"),
    severity: Severity | None = Query(default=None),
    user_id: str = Depends(current_user_id),
    service: InsightService = Depends(insight_service),
) -> dict:
    return success(
        await service.list_insights(user_id, portfolio_id=portfolio_id, severity=severity)
    )
