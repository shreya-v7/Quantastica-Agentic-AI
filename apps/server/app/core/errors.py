"""Typed application errors mapped to stable API error codes.

Every error carries a code from the contract enum. The central exception handler
turns these into the response envelope. Stack traces and secret values never reach
the client.
"""

from __future__ import annotations


class AppError(Exception):
    code: str = "INTERNAL_ERROR"
    status_code: int = 500

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    code = "NOT_FOUND"
    status_code = 404


class ValidationError(AppError):
    code = "VALIDATION_ERROR"
    status_code = 422


class LLMError(AppError):
    code = "LLM_ERROR"
    status_code = 502


class PlatformNotConfiguredError(AppError):
    code = "PLATFORM_NOT_CONFIGURED"
    status_code = 503

    def __init__(self, component: str, missing_env: list[str]):
        self.component = component
        self.missing_env = missing_env
        names = ", ".join(missing_env) if missing_env else "(none)"
        super().__init__(
            f"Component '{component}' is not configured. Missing env vars: {names}."
        )


class ProviderNotConfiguredError(AppError):
    code = "PROVIDER_NOT_CONFIGURED"
    status_code = 503

    def __init__(self, provider: str, missing_env: list[str]):
        self.provider = provider
        self.missing_env = missing_env
        names = ", ".join(missing_env) if missing_env else "(none)"
        super().__init__(
            f"Provider '{provider}' is not configured. Missing env vars: {names}."
        )


class ProviderUnavailableError(AppError):
    code = "PROVIDER_UNAVAILABLE"
    status_code = 503

    def __init__(self, provider: str, detail: str):
        self.provider = provider
        super().__init__(f"Provider '{provider}' is unavailable: {detail}")


class AuthRequiredError(AppError):
    code = "AUTH_REQUIRED"
    status_code = 401


class ForbiddenError(AppError):
    code = "FORBIDDEN"
    status_code = 403


class RateLimitedError(AppError):
    code = "RATE_LIMITED"
    status_code = 429

    def __init__(self, message: str, retry_after_seconds: int):
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


class LiveTradingDisabledError(AppError):
    code = "LIVE_TRADING_DISABLED"
    status_code = 403


class TradeLimitError(AppError):
    code = "TRADE_LIMIT_EXCEEDED"
    status_code = 422


class MarketClosedError(AppError):
    code = "MARKET_CLOSED"
    status_code = 422


class ConfigError(Exception):
    """Raised at startup when configuration is invalid. Aborts the process."""
