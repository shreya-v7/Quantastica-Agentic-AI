"""Application entry point. Wires settings, logging, middleware, routes, and the
central exception handler that maps typed errors to the response envelope."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app import __version__
from app.core.config import Settings, get_settings
from app.core.envelope import failure, success
from app.core.errors import AppError, RateLimitedError
from app.core.logging import configure_logging
from app.core.middleware import AuthMiddleware, RequestIdMiddleware
from app.core.observability import init_sentry
from app.infra.factory import build_container
from app.routes import (
    admin,
    agents,
    alerts,
    auth,
    automation,
    calc,
    chat,
    dev,
    documents,
    health,
    insights,
    market,
    match,
    platform,
    portfolios,
    profile,
    seed,
    trades,
    whatsapp,
)

logger = logging.getLogger("quantastica.app")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.app_env, settings.log_level)
    init_sentry(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        await app.state.container.close()

    app = FastAPI(
        title="Quantastica API",
        version=__version__,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.container = build_container(settings)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(AuthMiddleware, settings=settings)
    app.add_middleware(RequestIdMiddleware)

    for router in (
        health.router,
        platform.router,
        auth.router,
        profile.router,
        portfolios.router,
        insights.router,
        agents.router,
        market.router,
        calc.router,
        match.router,
        trades.router,
        automation.router,
        alerts.router,
        chat.router,
        documents.router,
        whatsapp.router,
        admin.router,
        seed.router,
    ):
        app.include_router(router, prefix="/api")

    if not settings.is_prod:
        app.include_router(dev.router)

    @app.get("/api/ready")
    async def ready(request: Request) -> JSONResponse:
        """Readiness: DB and Redis reachable. Deploys gate on this."""
        container = request.app.state.container
        checks: dict[str, bool] = {}
        try:
            engine = getattr(container.repository, "engine", None)
            async with engine.connect() as conn:  # type: ignore[union-attr]
                await conn.execute(text("SELECT 1"))
            checks["database"] = True
        except Exception:
            checks["database"] = False
        try:
            await container.cache.ping()
            checks["redis"] = True
        except Exception:
            checks["redis"] = False
        ok = all(checks.values())
        body = success({"ready": ok, "checks": checks})
        return JSONResponse(status_code=200 if ok else 503, content=body)

    _register_exception_handlers(app)
    logger.info(
        "Quantastica started: env=%s platform=%s ready=%s",
        settings.app_env,
        settings.platform.value,
        app.state.container.status().ready,
    )
    return app


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError) -> JSONResponse:
        headers = {}
        if isinstance(exc, RateLimitedError):
            headers["Retry-After"] = str(exc.retry_after_seconds)
        return JSONResponse(
            status_code=exc.status_code,
            content=failure(exc.code, exc.message),
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content=failure("VALIDATION_ERROR", str(exc.errors())))

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse(
            status_code=500,
            content=failure("INTERNAL_ERROR", "An unexpected error occurred."),
        )


app = create_app()
