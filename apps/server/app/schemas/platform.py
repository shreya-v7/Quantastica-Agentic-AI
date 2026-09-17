from typing import Literal

from app.schemas.base import Contract
from app.schemas.common import Platform

ComponentName = Literal["repository", "llm", "events", "storage", "cache"]


class ComponentStatus(Contract):
    name: ComponentName
    implementation: str
    ready: bool
    missing_env: list[str]


class ProviderStatus(Contract):
    name: str
    implementation: str
    ready: bool
    missing_env: list[str]


class PlatformStatus(Contract):
    platform: Platform
    app_env: Literal["dev", "prod"]
    ready: bool
    components: list[ComponentStatus]
    providers: list[ProviderStatus]


class HealthStatus(Contract):
    status: Literal["ok"]
    version: str
