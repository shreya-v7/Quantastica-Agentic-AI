"""FastAPI dependency providers."""

from __future__ import annotations

from fastapi import Depends, Request

from app.core.config import Settings
from app.core.errors import AuthRequiredError
from app.core.security import verify_token
from app.infra.factory import Container
from app.services.agent_service import AgentService
from app.services.insight_service import InsightService
from app.services.portfolio_service import PortfolioService

DEV_USER_ID = "usr_seed_arjun"


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_container(request: Request) -> Container:
    return request.app.state.container


def current_user_id(request: Request, settings: Settings = Depends(get_settings)) -> str:
    """Resolve the authenticated user. In dev without auth, requests act as the seed
    user so the product is explorable immediately after `make seed`."""
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        claims = verify_token(settings, header[len("Bearer ") :])
        return str(claims["sub"])
    if not settings.auth_enabled:
        return DEV_USER_ID
    raise AuthRequiredError("Missing bearer token")


def portfolio_service(container: Container = Depends(get_container)) -> PortfolioService:
    return PortfolioService(container.repository)


def insight_service(container: Container = Depends(get_container)) -> InsightService:
    return InsightService(container.repository)


def agent_service(container: Container = Depends(get_container)) -> AgentService:
    return AgentService(container)
