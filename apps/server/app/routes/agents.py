from fastapi import APIRouter, Depends, Query

from app.core.dependencies import agent_service, current_user_id
from app.core.envelope import success
from app.schemas.agents import RunRequest
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agents")


@router.post("/run")
async def run_agents(
    body: RunRequest,
    user_id: str = Depends(current_user_id),
    service: AgentService = Depends(agent_service),
) -> dict:
    run = await service.run(user_id, query=body.query, portfolio_id=body.portfolio_id)
    return success(run)


@router.get("/runs")
async def list_runs(
    portfolio_id: str | None = Query(default=None, alias="portfolioId"),
    user_id: str = Depends(current_user_id),
    service: AgentService = Depends(agent_service),
) -> dict:
    return success(await service.list_runs(user_id, portfolio_id=portfolio_id))


@router.get("/runs/{run_id}")
async def get_run(
    run_id: str,
    user_id: str = Depends(current_user_id),
    service: AgentService = Depends(agent_service),
) -> dict:
    return success(await service.get_run(user_id, run_id))


@router.post("/runs/{run_id}/export")
async def export_run(
    run_id: str,
    user_id: str = Depends(current_user_id),
    service: AgentService = Depends(agent_service),
) -> dict:
    return success(await service.export_run(user_id, run_id))
