import importlib
import sys

from tests.helpers import build_settings


def test_runtime_orchestration_exports_broker_from_settings(monkeypatch) -> None:
    captured: dict[str, object] = {}
    settings = build_settings(
        db={"redis_url": "redis://cache.example:6379/7"},
        broker={
            "taskiq_queue_name": "registries:test",
            "taskiq_consumer_group_name": "registries:consumer",
        },
    )

    monkeypatch.setattr("core.settings.get_settings", lambda: settings)
    monkeypatch.setattr(
        "taskiq_redis.RedisStreamBroker",
        lambda *, url, queue_name, consumer_group_name: {
            "url": url,
            "queue_name": queue_name,
            "consumer_group_name": consumer_group_name,
        },
    )
    sys.modules.pop("runtime.orchestration.broker", None)
    sys.modules.pop("runtime.orchestration", None)

    runtime_orchestration_module = importlib.import_module("runtime.orchestration")

    assert runtime_orchestration_module.broker == {
        "url": "redis://cache.example:6379/7",
        "queue_name": "registries:test",
        "consumer_group_name": "registries:consumer",
    }
