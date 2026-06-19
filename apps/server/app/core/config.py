"""Twelve-factor configuration. All config comes from env vars and is validated at startup.

In prod the process refuses to start when required vars are missing, naming each one.
In dev the process starts degraded and reports honest readiness on GET /api/platform.
PostgreSQL and Redis are used on every platform; PLATFORM selects the LLM and object
storage implementations.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.errors import ConfigError
from app.schemas.common import Platform

COMPONENTS = ("repository", "llm", "events", "storage", "cache")

# Required env vars per component. DATABASE_URL and REDIS_URL ship dev defaults, so in
# dev these are always satisfied; readiness of the actual connection is reported by
# GET /api/ready.
COMPONENT_REQUIREMENTS: dict[str, dict[Platform, list[str]]] = {
    "repository": {p: ["DATABASE_URL"] for p in Platform},
    "events": {p: ["REDIS_URL"] for p in Platform},
    "cache": {p: ["REDIS_URL"] for p in Platform},
    "llm": {
        Platform.local: ["ANTHROPIC_API_KEY"],
        Platform.gcp: ["GCP_PROJECT", "GCP_REGION", "VERTEX_MODEL"],
        Platform.aws: ["AWS_REGION", "BEDROCK_MODEL_ID"],
    },
    "storage": {
        Platform.local: [],
        Platform.gcp: ["GCS_BUCKET"],
        Platform.aws: ["AWS_REGION", "S3_BUCKET"],
    },
}

IMPLEMENTATION_NAMES: dict[str, dict[Platform, str]] = {
    "repository": {p: "postgres" for p in Platform},
    "events": {p: "redis-streams" for p in Platform},
    "cache": {p: "redis" for p in Platform},
    "llm": {Platform.local: "anthropic", Platform.gcp: "vertex", Platform.aws: "bedrock"},
    "storage": {Platform.local: "disk", Platform.gcp: "gcs", Platform.aws: "s3"},
}

# Cross-platform providers: name -> required env vars (empty = key-free, always ready).
PROVIDER_REQUIREMENTS: dict[str, list[str]] = {
    "marketdata": [],
    "mfdata": [],
    "news": ["NEWSAPI_KEY"],
    "broker_paper": [],
    "broker_live": ["KITE_API_KEY", "KITE_API_SECRET", "KITE_ACCESS_TOKEN"],
    "whatsapp": ["WHATSAPP_TOKEN", "WHATSAPP_PHONE_ID", "WHATSAPP_VERIFY_TOKEN"],
    "embeddings": ["VOYAGE_API_KEY"],
    "aa": ["AA_CLIENT_ID", "AA_CLIENT_SECRET", "AA_BASE_URL"],
}

MIN_JWT_SECRET_BYTES = 32


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: Literal["dev", "prod"] = "dev"
    platform: Platform = Platform.local
    log_level: str = "INFO"

    # Auth
    require_auth: bool = False
    jwt_secret: str | None = None
    jwt_algorithm: str = "HS256"
    access_token_ttl_seconds: int = 15 * 60
    refresh_token_ttl_seconds: int = 30 * 24 * 3600
    fresh_auth_window_seconds: int = 5 * 60
    login_max_attempts: int = Field(default=5, ge=1)
    login_lock_minutes: int = Field(default=15, ge=1)

    # Rate limits (requests per window per identity)
    rate_limit_default: int = Field(default=120, ge=1)
    rate_limit_window_seconds: int = Field(default=60, ge=1)
    rate_limit_auth: int = Field(default=10, ge=1)
    rate_limit_money: int = Field(default=30, ge=1)

    # CORS (comma separated). prod refuses "*".
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Seed endpoints
    allow_seed: bool = False

    # Data stores (every platform)
    database_url: str = "postgresql+asyncpg://quantastica:quantastica@localhost:5432/quantastica"
    db_pool_size: int = Field(default=10, ge=1)
    redis_url: str = "redis://localhost:6379/0"

    # LLM
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-haiku-20241022"
    gcp_project: str | None = None
    gcp_region: str | None = None
    vertex_model: str | None = None
    aws_region: str | None = None
    bedrock_model_id: str | None = None
    llm_max_tokens: int = Field(default=2048, ge=256)
    llm_retries: int = Field(default=1, ge=0)
    llm_daily_token_budget: int = Field(default=200_000, ge=1000)

    # Object storage
    storage_dir: str = "./var/exports"
    s3_bucket: str | None = None
    s3_endpoint_url: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    gcs_bucket: str | None = None

    # Providers
    newsapi_key: str | None = None
    voyage_api_key: str | None = None
    kite_api_key: str | None = None
    kite_api_secret: str | None = None
    kite_access_token: str | None = None
    whatsapp_token: str | None = None
    whatsapp_phone_id: str | None = None
    whatsapp_verify_token: str | None = None
    whatsapp_app_secret: str | None = None
    aa_client_id: str | None = None
    aa_client_secret: str | None = None
    aa_base_url: str | None = None

    # Trading (paper is the default everywhere; live requires prod + gates)
    trading_mode: Literal["paper", "live"] = "paper"
    trade_max_order_notional_inr: float = Field(default=500_000.0, gt=0)
    trade_max_daily_notional_inr: float = Field(default=2_000_000.0, gt=0)
    trade_max_open_intents: int = Field(default=10, ge=1)
    automation_hard_max_notional_inr: float = Field(default=200_000.0, gt=0)
    automation_hard_max_executions_per_day: int = Field(default=20, ge=1)
    automation_hard_max_daily_notional_inr: float = Field(default=1_000_000.0, gt=0)

    # Worker
    worker_poll_seconds: float = Field(default=15.0, gt=0)

    # Observability
    sentry_dsn: str | None = None
    sentry_traces_sample_rate: float = Field(default=0.0, ge=0.0, le=1.0)

    @field_validator("cors_origins")
    @classmethod
    def _strip(cls, value: str) -> str:
        return value.strip()

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_prod(self) -> bool:
        return self.app_env == "prod"

    @property
    def auth_enabled(self) -> bool:
        return self.is_prod or self.require_auth

    @property
    def docs_enabled(self) -> bool:
        return not self.is_prod

    @property
    def seed_enabled(self) -> bool:
        return not self.is_prod or self.allow_seed

    @property
    def live_trading_configured(self) -> bool:
        return (
            self.is_prod
            and self.trading_mode == "live"
            and not self.missing_env_for_provider("broker_live")
        )

    def env_value(self, name: str) -> str | None:
        return getattr(self, name.lower(), None)

    def missing_env_for(self, component: str) -> list[str]:
        required = COMPONENT_REQUIREMENTS[component][self.platform]
        return [name for name in required if not self.env_value(name)]

    def missing_env_for_provider(self, provider: str) -> list[str]:
        return [name for name in PROVIDER_REQUIREMENTS[provider] if not self.env_value(name)]

    def implementation_for(self, component: str) -> str:
        return IMPLEMENTATION_NAMES[component][self.platform]

    @model_validator(mode="after")
    def _validate_prod(self) -> Settings:
        if not self.is_prod:
            return self

        problems: list[str] = []

        if "*" in self.cors_origin_list or not self.cors_origin_list:
            problems.append(
                "CORS_ORIGINS must be an explicit list in prod (wildcard '*' is refused)"
            )

        if not self.jwt_secret or len(self.jwt_secret.encode("utf-8")) < MIN_JWT_SECRET_BYTES:
            problems.append(
                f"JWT_SECRET must be at least {MIN_JWT_SECRET_BYTES} bytes in prod"
            )

        for component in COMPONENTS:
            for name in self.missing_env_for(component):
                problems.append(f"{name} (required for {self.platform.value} {component})")

        if self.trading_mode == "live":
            for name in self.missing_env_for_provider("broker_live"):
                problems.append(f"{name} (required for TRADING_MODE=live)")

        if problems:
            joined = "\n  - ".join(problems)
            raise ConfigError(f"Invalid prod configuration:\n  - {joined}")

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
