from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from core.settings import get_settings

_async_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_async_engine() -> AsyncEngine:
    """Return the process-level async engine, initializing it lazily on first use."""
    global _async_engine

    if _async_engine is None:
        settings = get_settings()
        _async_engine = create_async_engine(
            settings.db.postgres_dsn,
            future=True,
            pool_pre_ping=True,
        )

    return _async_engine


def get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    global _async_session_factory

    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            bind=get_async_engine(),
            autoflush=False,
            expire_on_commit=False,
        )

    return _async_session_factory


def AsyncSessionLocal() -> AsyncSession:
    return get_async_session_factory()()


async def dispose_async_engine() -> None:
    """Dispose the lazily-created engine and reset session factory state."""
    global _async_engine, _async_session_factory

    engine = _async_engine
    _async_engine = None
    _async_session_factory = None
    if engine is not None:
        await engine.dispose()


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


async def ping_database() -> None:
    async with get_async_engine().connect() as connection:
        await connection.execute(text("SELECT 1"))


__all__ = [
    "AsyncSessionLocal",
    "dispose_async_engine",
    "get_async_engine",
    "get_async_session_factory",
    "get_db_session",
    "ping_database",
]
