from __future__ import annotations

import asyncio
import importlib
import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any, Literal, cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parent.parent
BACKEND_ROOT = ROOT / "src" / "backend"
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


def _dispose_async_engine(engine: Any) -> None:
    asyncio.run(engine.dispose())


def _build_test_env() -> dict[str, str]:
    return {
        "OBSERVABILITY__LOGS_ENABLED": "false",
        "OBSERVABILITY__TRACES_ENABLED": "false",
        "OBSERVABILITY__SENTRY_ENABLED": "false",
        "OBSERVABILITY__METRICS_ENABLED": "false",
    }


def _build_readiness_payload(
    *,
    status: Literal["ok", "error"],
    service_name: str,
) -> Any:
    contracts_module = importlib.import_module("apps.system.contracts")
    dependency_probe = contracts_module.DependencyProbe
    readiness_probe = contracts_module.ReadinessProbe

    if status == "ok":
        checks = (
            dependency_probe(name="postgres", status="ok", detail=None),
            dependency_probe(name="redis", status="ok", detail=None),
        )
    else:
        checks = (
            dependency_probe(name="postgres", status="error", detail="database unavailable"),
            dependency_probe(name="redis", status="ok", detail=None),
        )

    return readiness_probe(status=status, service=service_name, checks=checks)


@pytest.fixture()
def app_factory() -> Iterator[Callable[..., FastAPI]]:
    runtimes: list[tuple[pytest.MonkeyPatch, object]] = []

    def factory(*, health_status: Literal["ok", "error"] = "ok") -> FastAPI:
        monkeypatch = pytest.MonkeyPatch()
        for key, value in _build_test_env().items():
            monkeypatch.setenv(key, value)

        _clear_settings_cache()
        _reload_backend_modules()
        _clear_settings_cache()

        bootstrap_module = importlib.import_module("core.bootstrap.app")
        deps_module = importlib.import_module("apps.system.api.deps")
        session_module = importlib.import_module("core.db.session")
        settings_module = importlib.import_module("core.settings")
        settings = settings_module.get_settings()

        liveness_probe = importlib.import_module("apps.system.contracts").LivenessProbe

        class FakeSystemStatusService:
            async def get_liveness(self) -> Any:
                return liveness_probe(service=settings.app.name)

            async def get_readiness(self) -> Any:
                return _build_readiness_payload(
                    status=health_status,
                    service_name=settings.app.name,
                )

        app = cast(FastAPI, bootstrap_module.create_app())
        app.dependency_overrides[deps_module.get_system_status_service] = FakeSystemStatusService
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
