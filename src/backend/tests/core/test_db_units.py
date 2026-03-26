from collections.abc import AsyncIterator
from types import SimpleNamespace
from typing import Any, cast

import pytest
from core.db import session as db_session_module
from core.db import uow as db_uow_module
from core.db.base import NAMING_CONVENTION
from core.db.persistence import AsyncQueryService, AsyncRepository, PersistenceComponent
from core.db.session import dispose_async_engine, get_async_engine, get_db_session, ping_database
from core.db.uow import AsyncUnitOfWork, BaseAsyncUnitOfWork, SessionUnitOfWork, async_session_scope, get_uow
from tests.helpers import run_async


class _FakeSession:
    def __init__(self, *, in_transaction: bool = False) -> None:
        self._in_transaction = in_transaction
        self.commit_calls = 0
        self.rollback_calls = 0
        self.flush_calls = 0
        self.close_calls = 0

    def in_transaction(self) -> bool:
        return self._in_transaction

    async def commit(self) -> None:
        self.commit_calls += 1
        self._in_transaction = False

    async def rollback(self) -> None:
        self.rollback_calls += 1
        self._in_transaction = False

    async def flush(self) -> None:
        self.flush_calls += 1

    async def close(self) -> None:
        self.close_calls += 1


def test_persistence_components_expose_session_and_component_name() -> None:
    session = cast(Any, object())
    component = PersistenceComponent(session, component_name="component")
    repository = AsyncRepository(session, repository_name="repository")
    query_service = AsyncQueryService(session, service_name="query-service")

    assert NAMING_CONVENTION["pk"] == "pk_%(table_name)s"
    assert component.session is session
    assert component.component_name == "component"
    assert repository.component_name == "repository"
    assert query_service.component_name == "query-service"


def test_get_db_session_yields_and_closes_session(monkeypatch: pytest.MonkeyPatch) -> None:
    session = _FakeSession()
    monkeypatch.setattr(db_session_module, "AsyncSessionLocal", lambda: session)

    async def scenario() -> None:
        generator = get_db_session()
        yielded = await anext(generator)

        assert cast(Any, yielded) is session

        with pytest.raises(StopAsyncIteration):
            await anext(generator)

    run_async(scenario())

    assert session.close_calls == 1


def test_ping_database_executes_probe_query(monkeypatch: pytest.MonkeyPatch) -> None:
    executed: list[str] = []

    class FakeConnection:
        async def execute(self, statement: object) -> None:
            executed.append(str(statement))

    class FakeConnectionContext:
        async def __aenter__(self) -> FakeConnection:
            return FakeConnection()

        async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
            return None

    monkeypatch.setattr(
        db_session_module, "get_async_engine", lambda: SimpleNamespace(connect=lambda: FakeConnectionContext())
    )

    run_async(ping_database())

    assert executed == ["SELECT 1"]


def test_async_engine_is_created_lazily_and_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    created: list[str] = []
    fake_engine = object()

    def fake_create_async_engine(dsn: str, *, future: bool, pool_pre_ping: bool) -> object:
        assert future is True
        assert pool_pre_ping is True
        created.append(dsn)
        return fake_engine

    monkeypatch.setattr(db_session_module, "_async_engine", None)
    monkeypatch.setattr(db_session_module, "_async_session_factory", None)
    monkeypatch.setattr(
        db_session_module,
        "get_settings",
        lambda: SimpleNamespace(db=SimpleNamespace(postgres_dsn="postgresql+asyncpg://lazy:test@localhost/lazy")),
    )
    monkeypatch.setattr(
        db_session_module,
        "create_async_engine",
        fake_create_async_engine,
    )

    assert created == []
    assert get_async_engine() is fake_engine
    assert get_async_engine() is fake_engine
    assert created == ["postgresql+asyncpg://lazy:test@localhost/lazy"]


def test_dispose_async_engine_resets_cached_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeEngine:
        def __init__(self) -> None:
            self.dispose_calls = 0

        async def dispose(self) -> None:
            self.dispose_calls += 1

    engine = FakeEngine()
    monkeypatch.setattr(db_session_module, "_async_engine", cast(Any, engine))
    monkeypatch.setattr(db_session_module, "_async_session_factory", cast(Any, object()))

    run_async(dispose_async_engine())

    assert engine.dispose_calls == 1
    assert db_session_module._async_engine is None
    assert db_session_module._async_session_factory is None


def test_base_async_unit_of_work_proxies_session_methods() -> None:
    session = _FakeSession()
    uow = BaseAsyncUnitOfWork(cast(Any, session), owns_session=False)

    async def scenario() -> None:
        assert (await uow.__aenter__()) is uow
        await uow.commit()
        await uow.rollback()
        await uow.flush()

    run_async(scenario())

    assert cast(Any, uow.session) is session
    assert session.commit_calls == 1
    assert session.rollback_calls == 1
    assert session.flush_calls == 1


def test_base_async_unit_of_work_rolls_back_and_closes_owned_session() -> None:
    session = _FakeSession(in_transaction=True)

    async def scenario() -> None:
        async with BaseAsyncUnitOfWork(cast(Any, session), owns_session=True):
            pass

    run_async(scenario())

    assert session.rollback_calls == 1
    assert session.close_calls == 1


def test_base_async_unit_of_work_does_not_commit_implicitly() -> None:
    session = _FakeSession(in_transaction=True)

    async def scenario() -> None:
        async with BaseAsyncUnitOfWork(cast(Any, session), owns_session=True):
            pass

    run_async(scenario())

    assert session.commit_calls == 0
    assert session.rollback_calls == 1
    assert session.close_calls == 1


def test_base_async_unit_of_work_rolls_back_on_exception() -> None:
    session = _FakeSession()

    async def scenario() -> None:
        async with BaseAsyncUnitOfWork(cast(Any, session), owns_session=True):
            raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        run_async(scenario())

    assert session.rollback_calls == 1
    assert session.close_calls == 1


def test_base_async_unit_of_work_respects_explicit_commit() -> None:
    session = _FakeSession(in_transaction=True)

    async def scenario() -> None:
        async with BaseAsyncUnitOfWork(cast(Any, session), owns_session=True) as uow:
            await uow.commit()

    run_async(scenario())

    assert session.commit_calls == 1
    assert session.rollback_calls == 0
    assert session.close_calls == 1


def test_base_async_unit_of_work_handles_sessions_without_transaction_method() -> None:
    uow = BaseAsyncUnitOfWork(cast(Any, object()), owns_session=False)

    assert uow._transaction_is_open() is False


def test_async_unit_of_work_uses_session_factory(monkeypatch: pytest.MonkeyPatch) -> None:
    session = _FakeSession()
    monkeypatch.setattr(db_uow_module, "AsyncSessionLocal", lambda: session)

    uow = AsyncUnitOfWork()

    assert cast(Any, uow.session) is session


def test_session_unit_of_work_keeps_external_session_open() -> None:
    session = _FakeSession()

    async def scenario() -> None:
        async with SessionUnitOfWork(cast(Any, session)):
            pass

    run_async(scenario())

    assert session.close_calls == 0


def test_get_uow_yields_context_managed_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    events: list[str] = []

    class FakeAsyncUnitOfWork:
        def __init__(self) -> None:
            events.append("init")

        async def __aenter__(self) -> str:
            events.append("enter")
            return "uow"

        async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
            events.append("exit")

    monkeypatch.setattr(db_uow_module, "AsyncUnitOfWork", FakeAsyncUnitOfWork)

    async def scenario() -> None:
        generator: AsyncIterator[Any] = get_uow()
        assert await anext(generator) == "uow"
        with pytest.raises(StopAsyncIteration):
            await anext(generator)

    run_async(scenario())

    assert events == ["init", "enter", "exit"]


def test_async_session_scope_yields_underlying_session(monkeypatch: pytest.MonkeyPatch) -> None:
    session = object()
    events: list[str] = []

    class FakeAsyncUnitOfWork:
        def __init__(self) -> None:
            self.session = session

        async def __aenter__(self) -> FakeAsyncUnitOfWork:
            events.append("enter")
            return self

        async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
            events.append("exit")

    monkeypatch.setattr(db_uow_module, "AsyncUnitOfWork", FakeAsyncUnitOfWork)

    async def scenario() -> None:
        async with async_session_scope() as scoped_session:
            assert scoped_session is session

    run_async(scenario())

    assert events == ["enter", "exit"]
