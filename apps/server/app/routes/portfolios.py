from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response

from app.core.dependencies import current_user_id, portfolio_service
from app.core.envelope import success
from app.core.http import etag_json
from app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/portfolios")


@router.get("")
async def list_portfolios(
    user_id: str = Depends(current_user_id),
    service: PortfolioService = Depends(portfolio_service),
) -> dict:
    return success(await service.list_portfolios(user_id))


@router.get("/{portfolio_id}")
async def get_portfolio(
    portfolio_id: str,
    request: Request,
    user_id: str = Depends(current_user_id),
    service: PortfolioService = Depends(portfolio_service),
) -> Response:
    detail = await service.get_detail(user_id, portfolio_id)
    return etag_json(request, detail)
