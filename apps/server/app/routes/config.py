"""Public config — feature flags + contract version (SSOT for runtime behavior)."""

from __future__ import annotations

import os

from fastapi import APIRouter

from app.contracts.models import ConfigResponse, DemoFlags, FeatureFlags
from app.contracts.version import CONTRACT_VERSION
from app.financial_intelligence.cloud.config import CLOUD

router = APIRouter(tags=["Config"])


def _env_bool(key: str, default: str = "true") -> bool:
    return os.getenv(key, default).lower() in ("1", "true", "yes", "on")


@router.get("/config", response_model=ConfigResponse)
def get_config() -> ConfigResponse:
    return ConfigResponse(
        version=CONTRACT_VERSION,
        flags=FeatureFlags(
            cloud=CLOUD,
            ai=_env_bool("FI_FEATURE_AI", "true"),
            insights=_env_bool("FI_FEATURE_INSIGHTS", "true"),
        ),
        demo=DemoFlags(enabled=_env_bool("FI_DEMO", "true")),
    )
