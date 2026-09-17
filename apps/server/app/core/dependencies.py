"""FastAPI dependency providers: settings, container, current user, rate limiting,
fresh-auth enforcement, and service construction."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Depends, Request

from app.core.config import Settings
from app.core.errors import AuthRequiredError, ForbiddenError
from app.core.security import is_fresh, verify_token
from app.infra.factory import Container
from app.infra.repo.auth_repo import AuthRepository
from app.services.agent_service import AgentService
from app.services.auth_service import AuthService
from app.services.insight_service import InsightService
from app.services.portfolio_service import PortfolioService

FIRM_ROLES = ("admin", "adviser", "reviewer", "read_only")
_ROLE_ALIAS = {"user": "adviser"}
DEV_USER_ID = "usr_seed_arjun"


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_container(request: Request) -> Container:
    return request.app.state.container


def client_ip(request: Request) -> str | None:
    if request.client:
        return request.client.host
    return None


def current_claims(request: Request, settings: Settings = Depends(get_settings)) -> dict:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return verify_token(settings, header[len("Bearer ") :])
    if not settings.auth_enabled:
        return {"sub": DEV_USER_ID, "role": "user", "iat": 0, "dev": True}
    raise AuthRequiredError("Missing bearer token")


def current_user_id(claims: dict = Depends(current_claims)) -> str:
    return str(claims["sub"])


def _firm_role(claims: dict) -> str:
    raw = str(claims.get("role") or "user")
    return _ROLE_ALIAS.get(raw, raw)


def require_admin(claims: dict = Depends(current_claims)) -> str:
    if _firm_role(claims) != "admin":
        raise ForbiddenError("Admin role required")
    return str(claims["sub"])


def require_role(*allowed: str):
    """Firm RBAC: admin, adviser, reviewer, read_only. Dev `user` maps to adviser."""

    def _dep(claims: dict = Depends(current_claims)) -> str:
        role = _firm_role(claims)
        if role not in allowed:
            raise ForbiddenError(f"Role '{role}' cannot perform this action")
        return str(claims["sub"])

    return _dep


def require_fresh_auth(
    claims: dict = Depends(current_claims), settings: Settings = Depends(get_settings)
) -> str:
    """Money-path guard. In dev without auth this is permissive; once authenticated the
    access token must have been minted within the fresh-auth window."""
    if claims.get("dev"):
        return str(claims["sub"])
    if not is_fresh(claims, settings.fresh_auth_window_seconds):
        raise AuthRequiredError(
            "This action needs a recent sign-in. Refresh your session and retry."
        )
    return str(claims["sub"])


def rate_limit(scope: str, kind: str = "default") -> Callable[..., Awaitable[None]]:
    """Build a dependency that consumes one token from a per-identity Redis window."""

    async def _dep(
        request: Request,
        container: Container = Depends(get_container),
        settings: Settings = Depends(get_settings),
    ) -> None:
        identity = request.headers.get("Authorization") or (
            request.client.host if request.client else "anon"
        )
        limit = {
            "auth": settings.rate_limit_auth,
            "money": settings.rate_limit_money,
        }.get(kind, settings.rate_limit_default)
        key = f"{scope}:{identity[:64]}"
        await container.rate_limiter.hit(key, limit, settings.rate_limit_window_seconds)

    return _dep


# --- service providers ------------------------------------------------------
def auth_service(
    container: Container = Depends(get_container),
    settings: Settings = Depends(get_settings),
) -> AuthService:
    return AuthService(AuthRepository(container.session_factory), settings)


def portfolio_service(container: Container = Depends(get_container)) -> PortfolioService:
    return PortfolioService(container.repository)


def insight_service(container: Container = Depends(get_container)) -> InsightService:
    return InsightService(container.repository)


def agent_service(container: Container = Depends(get_container)) -> AgentService:
    return AgentService(container)
