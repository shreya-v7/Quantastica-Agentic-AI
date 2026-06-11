"""Request id and auth middleware."""

from __future__ import annotations

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import Settings
from app.core.context import request_id_var
from app.core.envelope import failure
from app.core.errors import AuthRequiredError
from app.core.security import verify_token

PUBLIC_PATHS = ("/api/health", "/api/platform", "/dev/session")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        token = request_id_var.set(request_id)
        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)
        response.headers["X-Request-ID"] = request_id
        return response


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)
        if not self.settings.auth_enabled or not self._protected(request.url.path):
            return await call_next(request)

        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return self._reject("Missing bearer token")

        try:
            verify_token(self.settings, header[len("Bearer ") :])
        except AuthRequiredError as exc:
            return self._reject(exc.message)

        return await call_next(request)

    @staticmethod
    def _protected(path: str) -> bool:
        if not path.startswith("/api/"):
            return False
        return not any(path.startswith(public) for public in PUBLIC_PATHS)

    @staticmethod
    def _reject(message: str) -> JSONResponse:
        return JSONResponse(status_code=401, content=failure("AUTH_REQUIRED", message))
