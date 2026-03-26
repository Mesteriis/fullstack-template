from types import SimpleNamespace
from typing import Any, cast

import pytest
from core.bootstrap import system as bootstrap_system_module
from redis.asyncio import Redis
from tests.helpers import build_settings, run_async


def test_build_system_status_service_reuses_cached_redis_client(monkeypatch: pytest.MonkeyPatch) -> None:
    created_clients: list[str] = []
    fake_client = cast(Any, object())
    settings = build_settings(db={"redis_url": "redis://cache.example:6379/0"})
    fake_uow = cast(Any, SimpleNamespace(session=object()))

    def fake_from_url(redis_url: str) -> Any:
        created_clients.append(redis_url)
        return fake_client

    bootstrap_system_module._SYSTEM_REDIS_CLIENTS.clear()
    monkeypatch.setattr(
        bootstrap_system_module,
        "Redis",
        SimpleNamespace(from_url=fake_from_url),
    )

    first = bootstrap_system_module.build_system_status_service(settings=settings, uow=fake_uow)
    second = bootstrap_system_module.build_system_status_service(settings=settings, uow=fake_uow)

    assert created_clients == ["redis://cache.example:6379/0"]
    assert cast(Any, first.health_port)._redis_client is fake_client
    assert cast(Any, second.health_port)._redis_client is fake_client


def test_close_system_redis_clients_closes_and_clears_cache() -> None:
    class FakeRedisClient:
        def __init__(self) -> None:
            self.closed = False

        async def aclose(self) -> None:
            self.closed = True

    first = FakeRedisClient()
    second = FakeRedisClient()
    bootstrap_system_module._SYSTEM_REDIS_CLIENTS.clear()
    bootstrap_system_module._SYSTEM_REDIS_CLIENTS["redis://one"] = cast(Redis, first)
    bootstrap_system_module._SYSTEM_REDIS_CLIENTS["redis://two"] = cast(Redis, second)

    run_async(bootstrap_system_module.close_system_redis_clients())

    assert first.closed is True
    assert second.closed is True
    assert bootstrap_system_module._SYSTEM_REDIS_CLIENTS == {}
