"""Test fixtures. Postgres and Redis run in throwaway containers (testcontainers);
the LLM is the only faked component, injected as a test double."""

from __future__ import annotations

import pytest
from app.core.config import Settings
from app.infra.db.engine import build_engine, build_session_factory
from app.infra.db.models import Base
from app.infra.events.inprocess import InProcessEventPublisher
from app.infra.factory import ComponentSlot, Container, _register_providers
from app.infra.repo.postgres import PostgresRepository
from app.infra.storage.disk import DiskStorage
from app.main import create_app
from app.seed import loader
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import text
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from tests.fakes import FakeLLM


@pytest.fixture(scope="session")
def pg_url() -> str:
    with PostgresContainer("pgvector/pgvector:pg16") as pg:
        url = pg.get_connection_url().replace("psycopg2", "asyncpg")
        yield url


@pytest.fixture(scope="session")
def redis_url() -> str:
    with RedisContainer("redis:7-alpine") as redis:
        host = redis.get_container_host_ip()
        port = redis.get_exposed_port(6379)
        yield f"redis://{host}:{port}/0"


def make_settings(pg_url: str, redis_url: str, **overrides) -> Settings:
    base = {
        "app_env": "dev",
        "platform": "local",
        "anthropic_api_key": "test-key",
        "database_url": pg_url,
        "redis_url": redis_url,
    }
    base.update(overrides)
    return Settings(_env_file=None, **base)


@pytest.fixture
def fake_llm() -> FakeLLM:
    return FakeLLM()


@pytest.fixture
async def container(fake_llm: FakeLLM, tmp_path, pg_url: str, redis_url: str) -> Container:
    settings = make_settings(pg_url, redis_url, storage_dir=str(tmp_path / "exports"))
    engine = build_engine(settings.database_url, settings.db_pool_size)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    repo = PostgresRepository(build_session_factory(engine))
    repo.engine = engine  # type: ignore[attr-defined]
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    slots = {
        "repository": ComponentSlot(repo, True, [], "postgres"),
        "llm": ComponentSlot(fake_llm, True, [], "fake"),
        "events": ComponentSlot(InProcessEventPublisher(), True, [], "inprocess"),
        "storage": ComponentSlot(DiskStorage(str(tmp_path / "exports")), True, [], "disk"),
        "cache": ComponentSlot(redis, True, [], "redis"),
    }
    cont = Container(settings, slots)
    _register_providers(cont)
    await loader.load_into(repo)
    yield cont
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE'))
    await redis.flushdb()
    await cont.close()


@pytest.fixture
async def client(container: Container) -> AsyncClient:
    app = create_app(container.settings)
    app.state.container = container
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
