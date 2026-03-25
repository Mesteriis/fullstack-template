import asyncio
from collections.abc import Awaitable
from typing import Any, TypeVar

from core.settings import ApiSettings, AppSettings, BrokerSettings, DatabaseSettings, ObservabilitySettings, Settings

_T = TypeVar("_T")


def run_async[T](awaitable: Awaitable[_T]) -> _T:
    return asyncio.run(awaitable)


def build_settings(
    *,
    app: dict[str, Any] | None = None,
    api: dict[str, Any] | None = None,
    db: dict[str, Any] | None = None,
    broker: dict[str, Any] | None = None,
    observability: dict[str, Any] | None = None,
) -> Settings:
    settings = Settings()
    return settings.model_copy(
        update={
            "app": AppSettings.model_validate({**settings.app.model_dump(), **(app or {})}),
            "api": ApiSettings.model_validate({**settings.api.model_dump(), **(api or {})}),
            "db": DatabaseSettings.model_validate({**settings.db.model_dump(), **(db or {})}),
            "broker": BrokerSettings.model_validate({**settings.broker.model_dump(), **(broker or {})}),
            "observability": ObservabilitySettings.model_validate(
                {**settings.observability.model_dump(), **(observability or {})}
            ),
        }
    )
