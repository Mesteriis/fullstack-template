import asyncio
import time
from typing import Any

import pytest
from apps.system.application import services as system_services_module
from apps.system.application.services import SystemStatusService
from redis.exceptions import RedisError
from tests.helpers import build_settings, run_async


class _HealthyPort:
    async def ping_database(self) -> None:
        return None

    async def ping_redis(self) -> None:
        return None


class _TimeoutDatabasePort(_HealthyPort):
    async def ping_database(self) -> None:
        await asyncio.sleep(0.05)


class _FailingRedisPort(_HealthyPort):
    async def ping_redis(self) -> None:
        raise RedisError("redis unavailable")


class _TimeoutBothPort(_HealthyPort):
    async def ping_database(self) -> None:
        await asyncio.sleep(0.3)

    async def ping_redis(self) -> None:
        await asyncio.sleep(0.3)


class _CaptureLogger:
    def __init__(self, calls: list[tuple[str, dict[str, Any]]]) -> None:
        self._calls = calls

    def warning(self, event: str, **context: Any) -> None:
        self._calls.append((event, context))


def test_readiness_returns_timeout_probe_and_logs_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, dict[str, Any]]] = []
    service = SystemStatusService(
        settings=build_settings(system={"health_timeout_seconds": 0.01}),
        health_port=_TimeoutDatabasePort(),
    )

    monkeypatch.setattr(system_services_module, "SYSTEM_HEALTH_LOGGER", _CaptureLogger(calls))

    readiness = run_async(service.get_readiness())

    assert readiness.status == "error"
    assert readiness.checks[0].model_dump() == {"name": "postgres", "status": "error", "detail": "timeout"}
    assert readiness.checks[1].model_dump() == {"name": "redis", "status": "ok", "detail": None}
    assert calls == [
        (
            "System dependency probe timed out",
            {
                "dependency": "postgres",
                "timeout_seconds": 0.01,
                "exc_info": True,
            },
        )
    ]


def test_readiness_logs_failures_but_keeps_safe_api_details(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, dict[str, Any]]] = []
    service = SystemStatusService(
        settings=build_settings(system={"health_timeout_seconds": 0.5}),
        health_port=_FailingRedisPort(),
    )

    monkeypatch.setattr(system_services_module, "SYSTEM_HEALTH_LOGGER", _CaptureLogger(calls))

    readiness = run_async(service.get_readiness())

    assert readiness.status == "error"
    assert readiness.checks[0].model_dump() == {"name": "postgres", "status": "ok", "detail": None}
    assert readiness.checks[1].model_dump() == {"name": "redis", "status": "error", "detail": "redis unavailable"}
    assert calls == [
        (
            "System dependency probe failed",
            {
                "dependency": "redis",
                "timeout_seconds": 0.5,
                "exc_info": True,
            },
        )
    ]


def test_readiness_probes_run_concurrently_with_per_dependency_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, dict[str, Any]]] = []
    service = SystemStatusService(
        settings=build_settings(system={"health_timeout_seconds": 0.1}),
        health_port=_TimeoutBothPort(),
    )

    monkeypatch.setattr(system_services_module, "SYSTEM_HEALTH_LOGGER", _CaptureLogger(calls))

    started_at = time.perf_counter()
    readiness = run_async(service.get_readiness())
    elapsed = time.perf_counter() - started_at

    assert readiness.status == "error"
    assert tuple(check.model_dump() for check in readiness.checks) == (
        {"name": "postgres", "status": "error", "detail": "timeout"},
        {"name": "redis", "status": "error", "detail": "timeout"},
    )
    assert elapsed < 0.18
    assert len(calls) == 2
