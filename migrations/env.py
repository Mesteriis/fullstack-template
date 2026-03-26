from __future__ import annotations

import asyncio
from logging.config import fileConfig
from pathlib import Path
import sys

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, async_engine_from_config


BACKEND_ROOT = Path(__file__).resolve().parents[1] / "src" / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from core.db import Base
from core.settings import get_settings


config = context.config
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.db.postgres_dsn)

if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = context.config.attributes.get("connection")

    if isinstance(connectable, AsyncConnection):
        await connectable.run_sync(do_run_migrations)
        return

    if isinstance(connectable, Connection):
        do_run_migrations(connectable)
        return

    if isinstance(connectable, Engine):
        with connectable.connect() as connection:
            do_run_migrations(connection)
        connectable.dispose()
        return

    if isinstance(connectable, AsyncEngine):
        engine = connectable
    else:
        engine = async_engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    if not isinstance(connectable, AsyncEngine):
        await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
