import asyncio
import importlib
import sys
import time
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
import redis
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient
from testcontainers.core.container import DockerContainer
from testcontainers.postgres import PostgresContainer

BACKEND_ROOT = Path(__file__).resolve().parents[1]
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
        "REGISTRIES_DB__POSTGRES_DSN": postgres_dsn,
        "REGISTRIES_DB__REDIS_URL": redis_url,
        "REGISTRIES_OBSERVABILITY__LOGS_ENABLED": "false",
        "REGISTRIES_OBSERVABILITY__TRACES_ENABLED": "false",
        "REGISTRIES_OBSERVABILITY__SENTRY_ENABLED": "false",
        "REGISTRIES_OBSERVABILITY__METRICS_ENABLED": "true",
    }


def _dispose_async_engine(engine: object) -> None:
    asyncio.run(engine.dispose())


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
        username="registries",
        password="registries",
        dbname="registries",
    ) as container:
        yield container


@pytest.fixture(scope="session")
def redis_container() -> Iterator[DockerContainer]:
    with DockerContainer("redis:7-alpine").with_exposed_ports(6379) as container:
        _wait_for_redis(container.get_container_host_ip(), int(container.get_exposed_port(6379)))
        yield container


@pytest.fixture(scope="session")
def postgres_dsn(postgres_container: PostgresContainer) -> str:
    return postgres_container.get_connection_url(driver="asyncpg")


@pytest.fixture(scope="session")
def redis_url(redis_container: DockerContainer) -> str:
    return f"redis://{redis_container.get_container_host_ip()}:{redis_container.get_exposed_port(6379)}/0"


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
        app = bootstrap_module.create_app()
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
def settings(app: FastAPI) -> object:
    settings_module = importlib.import_module("core.settings")
    return settings_module.get_settings()


@pytest.fixture(scope="session")
def faker() -> Faker:
    return Faker()
