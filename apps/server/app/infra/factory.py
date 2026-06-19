"""Infrastructure factory.

PostgreSQL and Redis are wired on every platform. PLATFORM (local | gcp | aws) selects
the LLM and object storage implementations. Cross-platform providers (market data, AMFI,
news, broker, WhatsApp, embeddings, AA) are registered with honest readiness; a provider
missing its env vars raises a typed PROVIDER_NOT_CONFIGURED when used and is reported by
GET /api/platform.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from redis.asyncio import Redis

from app.core.config import COMPONENTS, PROVIDER_REQUIREMENTS, Settings
from app.core.errors import PlatformNotConfiguredError, ProviderNotConfiguredError
from app.infra.events.base import EventPublisher
from app.infra.llm.base import LLMClient
from app.infra.repo.base import Repository
from app.infra.storage.base import BlobStorage
from app.schemas.common import Platform
from app.schemas.platform import ComponentStatus, PlatformStatus, ProviderStatus

logger = logging.getLogger("quantastica.factory")


@dataclass
class ComponentSlot:
    instance: object | None
    ready: bool
    missing_env: list[str]
    implementation: str


@dataclass
class ProviderSlot:
    instance: object | None
    ready: bool
    missing_env: list[str]
    implementation: str


@dataclass
class Container:
    settings: Settings
    slots: dict[str, ComponentSlot]
    providers: dict[str, ProviderSlot] = field(default_factory=dict)

    def _require(self, name: str) -> object:
        slot = self.slots[name]
        if not slot.ready or slot.instance is None:
            raise PlatformNotConfiguredError(name, slot.missing_env)
        return slot.instance

    def provider(self, name: str) -> object:
        slot = self.providers[name]
        if not slot.ready or slot.instance is None:
            raise ProviderNotConfiguredError(name, slot.missing_env)
        return slot.instance

    @property
    def repository(self) -> Repository:
        return self._require("repository")  # type: ignore[return-value]

    @property
    def llm(self) -> LLMClient:
        inner: LLMClient = self._require("llm")  # type: ignore[assignment]
        cache_slot = self.slots.get("cache")
        if cache_slot is None or not cache_slot.ready or cache_slot.instance is None:
            return inner
        from app.infra.llm.cache import CachingLLM

        if getattr(self, "_llm_cached", None) is None or self._llm_inner is not inner:
            self._llm_inner = inner
            self._llm_cached = CachingLLM(inner, cache_slot.instance)
        return self._llm_cached

    @property
    def events(self) -> EventPublisher:
        return self._require("events")  # type: ignore[return-value]

    @property
    def storage(self) -> BlobStorage:
        return self._require("storage")  # type: ignore[return-value]

    @property
    def cache(self) -> Redis:
        return self._require("cache")  # type: ignore[return-value]

    @property
    def session_factory(self):
        return self.repository.session_factory  # type: ignore[attr-defined]

    @property
    def rate_limiter(self):
        from app.core.ratelimit import RateLimiter

        return RateLimiter(self.cache)

    def status(self) -> PlatformStatus:
        components = [
            ComponentStatus(
                name=name,
                implementation=slot.implementation,
                ready=slot.ready,
                missing_env=slot.missing_env,
            )
            for name, slot in self.slots.items()
        ]
        providers = [
            ProviderStatus(
                name=name,
                implementation=slot.implementation,
                ready=slot.ready,
                missing_env=slot.missing_env,
            )
            for name, slot in self.providers.items()
        ]
        return PlatformStatus(
            platform=self.settings.platform,
            app_env=self.settings.app_env,
            ready=all(s.ready for s in self.slots.values()),
            components=components,
            providers=providers,
        )

    async def close(self) -> None:
        repo_slot = self.slots.get("repository")
        if repo_slot and repo_slot.instance is not None:
            engine = getattr(repo_slot.instance, "engine", None)
            if engine is not None:
                await engine.dispose()
        cache_slot = self.slots.get("cache")
        if cache_slot and cache_slot.instance is not None:
            await cache_slot.instance.aclose()  # type: ignore[union-attr]


def build_container(settings: Settings) -> Container:
    slots: dict[str, ComponentSlot] = {}
    shared: dict[str, object] = {}

    for component in COMPONENTS:
        implementation = settings.implementation_for(component)
        missing = settings.missing_env_for(component)
        if missing:
            slots[component] = ComponentSlot(None, False, missing, implementation)
            continue
        try:
            instance = _build_component(settings, component, shared)
            slots[component] = ComponentSlot(instance, True, [], implementation)
        except Exception as exc:  # degrade in dev; prod has already validated env
            logger.warning("Failed to build %s (%s): %s", component, implementation, exc)
            slots[component] = ComponentSlot(None, False, missing, implementation)

    container = Container(settings=settings, slots=slots)
    _register_providers(container)
    return container


def _redis(settings: Settings, shared: dict[str, object]) -> Redis:
    if "redis" not in shared:
        shared["redis"] = Redis.from_url(settings.redis_url, decode_responses=True)
    return shared["redis"]  # type: ignore[return-value]


def _build_component(settings: Settings, component: str, shared: dict[str, object]) -> object:
    if component == "repository":
        from app.infra.db.engine import build_engine, build_session_factory
        from app.infra.repo.postgres import PostgresRepository

        engine = build_engine(settings.database_url, settings.db_pool_size)
        repo = PostgresRepository(build_session_factory(engine))
        repo.engine = engine  # type: ignore[attr-defined]
        return repo

    if component == "events":
        from app.infra.events.redis_streams import RedisStreamsPublisher

        return RedisStreamsPublisher(_redis(settings, shared))

    if component == "cache":
        return _redis(settings, shared)

    if component == "llm":
        return _build_llm(settings)

    return _build_storage(settings)


def _build_llm(settings: Settings) -> LLMClient:
    if settings.platform == Platform.gcp:
        from app.infra.llm.vertex import VertexClient

        return VertexClient(
            project=settings.gcp_project or "",
            region=settings.gcp_region or "",
            model=settings.vertex_model or "",
            max_tokens=settings.llm_max_tokens,
        )
    if settings.platform == Platform.aws:
        from app.infra.llm.bedrock import BedrockClient

        return BedrockClient(
            region=settings.aws_region or "",
            model_id=settings.bedrock_model_id or "",
            max_tokens=settings.llm_max_tokens,
        )
    from app.infra.llm.anthropic import AnthropicClient

    return AnthropicClient(
        api_key=settings.anthropic_api_key or "",
        model=settings.anthropic_model,
        max_tokens=settings.llm_max_tokens,
    )


def _build_storage(settings: Settings) -> BlobStorage:
    if settings.platform == Platform.gcp:
        from app.infra.storage.gcs import GcsStorage

        return GcsStorage(bucket=settings.gcs_bucket or "")
    if settings.platform == Platform.aws:
        from app.infra.storage.s3 import S3Storage

        return S3Storage(bucket=settings.s3_bucket or "", region=settings.aws_region)
    if settings.s3_endpoint_url and settings.s3_bucket:
        from app.infra.storage.s3 import S3Storage

        return S3Storage(
            bucket=settings.s3_bucket,
            endpoint_url=settings.s3_endpoint_url,
            access_key=settings.s3_access_key,
            secret_key=settings.s3_secret_key,
        )
    from app.infra.storage.disk import DiskStorage

    return DiskStorage(settings.storage_dir)


def _register_providers(container: Container) -> None:
    settings = container.settings
    builders = {
        "marketdata": _build_marketdata,
        "mfdata": _build_mfdata,
        "news": _build_news,
        "broker_paper": _build_broker_paper,
        "broker_live": _build_broker_live,
        "whatsapp": _build_whatsapp,
        "embeddings": _build_embeddings,
        "aa": _build_aa,
    }
    implementations = {
        "marketdata": "yahoo-nse-bse",
        "mfdata": "amfi",
        "news": "newsapi-in",
        "broker_paper": "paper-engine",
        "broker_live": "zerodha-kite",
        "whatsapp": (
            "dev-echo" if settings.missing_env_for_provider("whatsapp") else "meta-cloud-api"
        ),
        "embeddings": "voyage",
        "aa": "sahamati-aa",
    }
    for name in PROVIDER_REQUIREMENTS:
        missing = settings.missing_env_for_provider(name)
        impl = implementations[name]
        if name == "whatsapp" and missing and not settings.is_prod:
            # Dev echo channel is a real, logged channel when WhatsApp is unconfigured.
            container.providers[name] = ProviderSlot(
                builders[name](container), True, [], "dev-echo"
            )
            continue
        if missing:
            container.providers[name] = ProviderSlot(None, False, missing, impl)
            continue
        try:
            container.providers[name] = ProviderSlot(builders[name](container), True, [], impl)
        except Exception as exc:
            logger.warning("Failed to build provider %s: %s", name, exc)
            container.providers[name] = ProviderSlot(None, False, missing, impl)


def _build_marketdata(container: Container) -> object:
    from app.providers.marketdata.yahoo import YahooMarketData

    return YahooMarketData()


def _build_mfdata(container: Container) -> object:
    from app.providers.mfdata.amfi import AmfiMfData

    return AmfiMfData()


def _build_news(container: Container) -> object:
    from app.providers.news.newsapi import NewsApiIndia

    return NewsApiIndia(api_key=container.settings.newsapi_key or "")


def _build_broker_paper(container: Container) -> object:
    from app.providers.broker.paper import PaperBroker

    return PaperBroker(marketdata=container.provider("marketdata"))  # type: ignore[arg-type]


def _build_broker_live(container: Container) -> object:
    from app.providers.broker.kite import KiteBroker

    settings = container.settings
    return KiteBroker(
        api_key=settings.kite_api_key or "",
        api_secret=settings.kite_api_secret or "",
        access_token=settings.kite_access_token or "",
    )


def _build_whatsapp(container: Container) -> object:
    settings = container.settings
    if settings.missing_env_for_provider("whatsapp"):
        from app.providers.whatsapp.echo import EchoWhatsApp

        return EchoWhatsApp()
    from app.providers.whatsapp.meta import MetaWhatsApp

    return MetaWhatsApp(
        token=settings.whatsapp_token or "",
        phone_id=settings.whatsapp_phone_id or "",
    )


def _build_embeddings(container: Container) -> object:
    from app.providers.embeddings.voyage import VoyageEmbeddings

    return VoyageEmbeddings(api_key=container.settings.voyage_api_key or "")


def _build_aa(container: Container) -> object:
    from app.providers.aa.sahamati import SahamatiAA

    settings = container.settings
    return SahamatiAA(
        client_id=settings.aa_client_id or "",
        client_secret=settings.aa_client_secret or "",
        base_url=settings.aa_base_url or "",
    )
