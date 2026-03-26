from core.db import AsyncRepository
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class SystemHealthRepository(AsyncRepository):
    def __init__(self, session: AsyncSession, *, redis_client: Redis) -> None:
        super().__init__(session, repository_name="SystemHealthRepository")
        self._redis_client = redis_client

    async def ping_database(self) -> None:
        await self.session.execute(text("SELECT 1"))

    async def ping_redis(self) -> None:
        await self._redis_client.ping()


__all__ = ["SystemHealthRepository"]
