import asyncio
import importlib
import sys
import time
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import asyncpg
import pytest
import redis
from alembic.config import Config
from core.settings.base import Settings
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.core.container import DockerContainer
from testcontainers.postgres import PostgresContainer

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parents[1]
_MODULE_RELOAD_ORDER = (
    "core.settings.base",
    "core.settings",
    "core.db.session",
    "core.db.uow",
    "core.db",
    "core.observability.context",
    "core.observability.logging",
    "core.observability.error_tracking",
    "core.observability.metrics",
    "core.observability.middleware",
    "core.observability.tracing",
    "core.observability.setup",
    "core.observability",
    "core.bootstrap.system",
    "apps.system.api.deps",
    "apps.system.api.read_endpoints",
    "apps.system.api.router",
    "apps.system.api",
    "api.router",
    "api",
    "core.bootstrap.app",
    "core.bootstrap",
)

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _reload_backend_modules() -> None:
    for module_name in _MODULE_RELOAD_ORDER:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)


def _clear_settings_cache() -> None:
    settings_module = importlib.import_module("core.settings.base")
    settings_module.get_settings.cache_clear()


def _build_test_env(*, postgres_dsn: str, redis_url: str) -> dict[str, str]:
    return {
        "DB__POSTGRES_DSN": postgres_dsn,
        "DB__REDIS_URL": redis_url,
        "OBSERVABILITY__LOGS_ENABLED": "false",
        "OBSERVABILITY__TRACES_ENABLED": "false",
        "OBSERVABILITY__SENTRY_ENABLED": "false",
        "OBSERVABILITY__METRICS_ENABLED": "true",
    }


def _dispose_async_engine(engine: Any) -> None:
    asyncio.run(engine.dispose())


def _replace_database_name(dsn: str, database_name: str) -> str:
    url = make_url(dsn)
    return url.set(database=database_name).render_as_string(hide_password=False)


def _replace_database_name_for_asyncpg(dsn: str, database_name: str) -> str:
    url = make_url(dsn)
    return url.set(database=database_name, drivername="postgresql").render_as_string(hide_password=False)


async def _create_database(postgres_dsn: str, database_name: str) -> None:
    maintenance_dsn = _replace_database_name_for_asyncpg(postgres_dsn, "postgres")
    connection = await asyncpg.connect(maintenance_dsn)
    try:
        await connection.execute(f'CREATE DATABASE "{database_name}"')
    finally:
        await connection.close()


async def _drop_database(postgres_dsn: str, database_name: str) -> None:
    maintenance_dsn = _replace_database_name_for_asyncpg(postgres_dsn, "postgres")
    connection = await asyncpg.connect(maintenance_dsn)
    try:
        await connection.execute(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = $1 AND pid <> pg_backend_pid()",
            database_name,
        )
        await connection.execute(f'DROP DATABASE IF EXISTS "{database_name}"')
    finally:
        await connection.close()


def _wait_for_redis(host: str, port: int) -> None:
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        try:
            client = redis.Redis(host=host, port=port)
            if client.ping():
                client.close()
                return
            client.close()
        except redis.RedisError:
            time.sleep(0.1)
        else:
            time.sleep(0.1)
    msg = f"Redis test container did not become ready at {host}:{port}"
    raise RuntimeError(msg)


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    with PostgresContainer(
        "postgres:17-alpine",
        username="fullstack_template",
        password="fullstack_template",
        dbname="fullstack_template",
    ) as container:
        yield container


@pytest.fixture(scope="session")
def redis_container() -> Iterator[DockerContainer]:
    with DockerContainer("redis:7-alpine").with_exposed_ports(6379) as container:
        _wait_for_redis(container.get_container_host_ip(), int(container.get_exposed_port(6379)))
        yield container


@pytest.fixture(scope="session")
def postgres_dsn(postgres_container: PostgresContainer) -> str:
    return str(postgres_container.get_connection_url(driver="asyncpg"))


@pytest.fixture(scope="session")
def redis_url(redis_container: DockerContainer) -> str:
    return f"redis://{redis_container.get_container_host_ip()}:{redis_container.get_exposed_port(6379)}/0"


@pytest.fixture()
def alembic_database_dsn(postgres_dsn: str) -> Iterator[str]:
    database_name = f"alembic_test_{uuid4().hex}"
    asyncio.run(_create_database(postgres_dsn, database_name))
    try:
        yield _replace_database_name(postgres_dsn, database_name)
    finally:
        asyncio.run(_drop_database(postgres_dsn, database_name))


@pytest.fixture()
def alembic_engine(alembic_database_dsn: str) -> Iterator[AsyncEngine]:
    engine = create_async_engine(alembic_database_dsn, future=True, pool_pre_ping=True, poolclass=NullPool)
    try:
        yield engine
    finally:
        _dispose_async_engine(engine)


@pytest.fixture()
def alembic_config() -> Config:
    config = Config(str(REPO_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "migrations"))
    return config


@pytest.fixture()
def app_factory(postgres_dsn: str, redis_url: str) -> Iterator[Callable[..., FastAPI]]:
    runtimes: list[tuple[pytest.MonkeyPatch, object]] = []

    def factory(
        *,
        override_postgres_dsn: str | None = None,
        override_redis_url: str | None = None,
    ) -> FastAPI:
        monkeypatch = pytest.MonkeyPatch()
        for key, value in _build_test_env(
            postgres_dsn=override_postgres_dsn or postgres_dsn,
            redis_url=override_redis_url or redis_url,
        ).items():
            monkeypatch.setenv(key, value)

        _clear_settings_cache()
        _reload_backend_modules()
        _clear_settings_cache()

        bootstrap_module = importlib.import_module("core.bootstrap.app")
        session_module = importlib.import_module("core.db.session")
        app = cast(FastAPI, bootstrap_module.create_app())
        runtimes.append((monkeypatch, session_module.async_engine))
        return app

    try:
        yield factory
    finally:
        for monkeypatch, engine in reversed(runtimes):
            _dispose_async_engine(engine)
            monkeypatch.undo()
        _clear_settings_cache()


@pytest.fixture()
def app(app_factory: Callable[..., FastAPI]) -> FastAPI:
    return app_factory()


@pytest.fixture()
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def reverse(app: FastAPI) -> Callable[[str], str]:
    def _reverse(route_name: str) -> str:
        return str(app.url_path_for(route_name))

    return _reverse


@pytest.fixture()
def settings(app: FastAPI) -> Settings:
    settings_module = importlib.import_module("core.settings")
    return cast(Settings, settings_module.get_settings())


@pytest.fixture(scope="session")
def faker() -> Faker:
    return Faker()
