from apps.system.application.services import SystemStatusService
from apps.system.infrastructure.repositories import SystemHealthRepository
from redis.asyncio import Redis

from core.db.uow import BaseAsyncUnitOfWork
from core.settings import Settings

_SYSTEM_REDIS_CLIENTS: dict[str, Redis] = {}


def get_system_redis_client(redis_url: str) -> Redis:
    redis_client = _SYSTEM_REDIS_CLIENTS.get(redis_url)
    if redis_client is None:
        redis_client = Redis.from_url(redis_url)
        _SYSTEM_REDIS_CLIENTS[redis_url] = redis_client
    return redis_client


async def close_system_redis_clients() -> None:
    clients = tuple(_SYSTEM_REDIS_CLIENTS.values())
    _SYSTEM_REDIS_CLIENTS.clear()
    for client in clients:
        await client.aclose()


def build_system_status_service(*, settings: Settings, uow: BaseAsyncUnitOfWork) -> SystemStatusService:
    return SystemStatusService(
        settings=settings,
        health_port=SystemHealthRepository(
            uow.session,
            redis_client=get_system_redis_client(settings.db.redis_url),
        ),
    )


__all__ = ["build_system_status_service", "close_system_redis_clients", "get_system_redis_client"]
