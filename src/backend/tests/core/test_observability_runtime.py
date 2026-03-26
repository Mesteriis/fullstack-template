from collections.abc import Callable
from types import SimpleNamespace
from typing import Any, cast

import pytest
from core.observability import metrics as observability_metrics_module
from core.observability import middleware as observability_middleware_module
from core.observability import setup as observability_setup_module
from core.observability import tracing as observability_tracing_module
from core.observability.context import get_correlation_id, get_request_id
from fastapi import FastAPI
from starlette.types import Message, Receive, Scope, Send
from tests.helpers import build_settings, run_async


class _FakeSpanContext:
    def __init__(self, *, valid: bool) -> None:
        self.is_valid = valid
        self.trace_id = int("3" * 32, 16)
        self.span_id = int("4" * 16, 16)


class _FakeSpan:
    def __init__(self, *, valid: bool = True) -> None:
        self._span_context = _FakeSpanContext(valid=valid)
        self.attributes: dict[str, str] = {}

    def get_span_context(self) -> _FakeSpanContext:
        return self._span_context

    def set_attribute(self, key: str, value: str) -> None:
        self.attributes[key] = value


class _FakeProvider:
    def __init__(self, *, resource: object | None = None, sampler: object | None = None) -> None:
        self.resource = resource
        self.sampler = sampler
        self.processors: list[object] = []
        self.flushed = False

    def add_span_processor(self, processor: object) -> None:
        self.processors.append(processor)

    def force_flush(self) -> None:
        self.flushed = True


def test_setup_metrics_instruments_app_once_and_skips_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    app = FastAPI()
    events: list[str] = []

    class FakeInstrumentator:
        def __init__(self, **kwargs: object) -> None:
            events.append("init")

        def instrument(self, instrumented_app: FastAPI) -> FakeInstrumentator:
            events.append("instrument")
            return self

        def expose(self, exposed_app: FastAPI, *, endpoint: str, include_in_schema: bool) -> None:
            events.append("expose")

    monkeypatch.setattr(observability_metrics_module, "Instrumentator", FakeInstrumentator)

    observability_metrics_module.setup_metrics(app, build_settings(observability={"enabled": False}))
    observability_metrics_module.setup_metrics(app, build_settings())
    observability_metrics_module.setup_metrics(app, build_settings())

    assert events == ["init", "instrument", "expose"]


def test_request_context_middleware_handles_http_and_non_http_scopes(monkeypatch: pytest.MonkeyPatch) -> None:
    sent_messages: list[Message] = []
    span = _FakeSpan(valid=True)

    async def http_app(scope: Scope, receive: Receive, send: Send) -> None:
        assert scope["state"]["request_id"] == "request-1"
        assert scope["state"]["correlation_id"] == "correlation-1"
        await send({"type": "http.response.start", "status": 200, "headers": [(b"x-request-id", b"request-1")]})
        await send({"type": "http.response.body", "body": b"ok"})

    async def non_http_app(scope: Scope, receive: Receive, send: Send) -> None:
        sent_messages.append({"type": "non-http"})

    async def receive() -> Message:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: Message) -> None:
        sent_messages.append(message)

    middleware = observability_middleware_module.RequestContextMiddleware(
        http_app,
        request_id_header_name="X-Request-ID",
        correlation_id_header_name="X-Correlation-ID",
    )

    monkeypatch.setattr(cast(Any, observability_middleware_module).trace, "get_current_span", lambda: span)

    run_async(
        middleware(
            {
                "type": "http",
                "method": "GET",
                "path": "/",
                "headers": [(b"x-request-id", b"request-1"), (b"x-correlation-id", b"correlation-1")],
            },
            receive,
            send,
        )
    )
    run_async(
        observability_middleware_module.RequestContextMiddleware(
            non_http_app,
            request_id_header_name="X-Request-ID",
            correlation_id_header_name="X-Correlation-ID",
        )({"type": "websocket"}, receive, send)
    )

    response_headers = dict(sent_messages[0]["headers"])
    assert response_headers[b"x-request-id"] == b"request-1"
    assert response_headers[b"x-correlation-id"] == b"correlation-1"
    assert span.attributes == {"request.id": "request-1", "correlation.id": "correlation-1"}
    assert get_request_id() is None
    assert get_correlation_id() is None
    assert sent_messages[-1] == {"type": "non-http"}


def test_setup_request_context_is_idempotent() -> None:
    app = FastAPI()

    observability_middleware_module.setup_request_context(
        app,
        request_id_header_name="X-Request-ID",
        correlation_id_header_name="X-Correlation-ID",
    )
    first_count = len(app.user_middleware)
    observability_middleware_module.setup_request_context(
        app,
        request_id_header_name="X-Request-ID",
        correlation_id_header_name="X-Correlation-ID",
    )

    assert len(app.user_middleware) == first_count
    assert app.state.request_context_configured is True


def test_setup_observability_wires_components_once(monkeypatch: pytest.MonkeyPatch) -> None:
    app = FastAPI()
    settings = build_settings()
    calls: list[str] = []
    events: list[tuple[str, object]] = []

    monkeypatch.setattr(observability_setup_module, "setup_logging", lambda received_settings: calls.append("logging"))
    monkeypatch.setattr(
        observability_setup_module,
        "setup_error_tracking",
        lambda received_settings: calls.append("error_tracking"),
    )
    monkeypatch.setattr(
        observability_setup_module,
        "setup_request_context",
        lambda received_app, *, request_id_header_name, correlation_id_header_name: calls.append("request_context"),
    )
    monkeypatch.setattr(
        observability_setup_module,
        "setup_metrics",
        lambda received_app, received_settings: calls.append("metrics"),
    )
    monkeypatch.setattr(
        observability_setup_module,
        "setup_tracing",
        lambda received_app, received_settings: calls.append("tracing"),
    )
    monkeypatch.setattr(app, "add_event_handler", lambda event, handler: events.append((event, handler)))

    observability_setup_module.setup_observability(app, settings)
    observability_setup_module.setup_observability(app, settings)

    assert calls == ["logging", "error_tracking", "request_context", "metrics", "tracing"]
    assert events == [("shutdown", cast(Any, observability_setup_module).flush_error_tracking)]


def test_tracing_helpers_cover_provider_setup_and_flush(monkeypatch: pytest.MonkeyPatch) -> None:
    app = FastAPI()
    settings = build_settings(
        app={"name": "Platform API", "version": "2.0.0", "environment": "test"},
        observability={
            "enabled": True,
            "traces_enabled": True,
            "otlp_endpoint": "https://otel.example/v1/traces",
            "otlp_headers": "Authorization=Bearer token",
            "trace_sample_rate": 0.25,
        },
    )
    current_provider: dict[str, object] = {"provider": object()}
    calls: list[str] = []
    events: list[tuple[str, object]] = []

    def fake_get_tracer_provider() -> object:
        return current_provider["provider"]

    def fake_set_tracer_provider(provider: object) -> None:
        current_provider["provider"] = provider

    monkeypatch.setattr(observability_tracing_module, "_FASTAPI_INSTRUMENTED_APPS", set())
    monkeypatch.setattr(observability_tracing_module, "_TRACING_PROVIDER_CONFIGURED", False)
    monkeypatch.setattr(observability_tracing_module, "_SQLALCHEMY_INSTRUMENTED", False)
    monkeypatch.setattr(observability_tracing_module, "_REDIS_INSTRUMENTED", False)
    monkeypatch.setattr(cast(Any, observability_tracing_module).trace, "get_tracer_provider", fake_get_tracer_provider)
    monkeypatch.setattr(cast(Any, observability_tracing_module).trace, "set_tracer_provider", fake_set_tracer_provider)
    monkeypatch.setattr(observability_tracing_module, "TracerProvider", _FakeProvider)
    monkeypatch.setattr(
        observability_tracing_module, "Resource", SimpleNamespace(create=lambda attrs: ("resource", attrs))
    )
    monkeypatch.setattr(observability_tracing_module, "ParentBasedTraceIdRatio", lambda ratio: ("sampler", ratio))
    monkeypatch.setattr(
        observability_tracing_module,
        "OTLPSpanExporter",
        lambda *, endpoint, headers: ("exporter", endpoint, headers),
    )
    monkeypatch.setattr(observability_tracing_module, "BatchSpanProcessor", lambda exporter: ("processor", exporter))
    monkeypatch.setattr(
        observability_tracing_module,
        "FastAPIInstrumentor",
        SimpleNamespace(instrument_app=lambda instrumented_app, **kwargs: calls.append("fastapi")),
    )
    monkeypatch.setattr(
        observability_tracing_module,
        "SQLAlchemyInstrumentor",
        lambda: SimpleNamespace(instrument=lambda *, engine: calls.append("sqlalchemy")),
    )
    monkeypatch.setattr(
        observability_tracing_module,
        "RedisInstrumentor",
        lambda: SimpleNamespace(instrument=lambda: calls.append("redis")),
    )
    monkeypatch.setattr(observability_tracing_module, "get_async_engine", lambda: SimpleNamespace(sync_engine="engine"))
    monkeypatch.setattr(app, "add_event_handler", lambda event, handler: events.append((event, handler)))

    assert observability_tracing_module._parse_otlp_headers("") == {}
    assert observability_tracing_module._parse_otlp_headers("Authorization=Bearer token") == {
        "Authorization": "Bearer token"
    }
    assert observability_tracing_module._parse_otlp_headers("Authorization=Bearer token, ,X-Test=value") == {
        "Authorization": "Bearer token",
        "X-Test": "value",
    }
    with pytest.raises(ValueError):
        observability_tracing_module._parse_otlp_headers("broken")

    provider = observability_tracing_module._ensure_tracer_provider(settings)

    assert isinstance(provider, _FakeProvider)
    assert observability_tracing_module._resource_attributes(settings) == {
        "service.name": "Platform API",
        "service.version": "2.0.0",
        "deployment.environment": "test",
    }

    observability_tracing_module.setup_tracing(app, build_settings(observability={"enabled": False}))
    observability_tracing_module.setup_tracing(
        app,
        build_settings(observability={"enabled": True, "traces_enabled": True, "otlp_endpoint": ""}),
    )
    observability_tracing_module.setup_tracing(app, settings)
    observability_tracing_module.setup_tracing(app, settings)
    current_provider["provider"] = provider
    observability_tracing_module.flush_tracing()

    assert calls == ["fastapi", "sqlalchemy", "redis"]
    assert events == [("shutdown", observability_tracing_module.flush_tracing)]
    assert provider.flushed is True
