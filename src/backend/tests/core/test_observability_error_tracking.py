from types import SimpleNamespace

import pytest
from core.observability import error_tracking as error_tracking_module
from core.observability.context import (
    reset_correlation_id,
    reset_request_id,
    set_correlation_id,
    set_request_id,
)
from tests.helpers import build_settings


class _FakeSpanContext:
    def __init__(self, *, valid: bool) -> None:
        self.is_valid = valid
        self.trace_id = int("1" * 32, 16)
        self.span_id = int("2" * 16, 16)


class _FakeSpan:
    def __init__(self, *, valid: bool) -> None:
        self._span_context = _FakeSpanContext(valid=valid)

    def get_span_context(self) -> _FakeSpanContext:
        return self._span_context


class _FakeScope:
    def __init__(self) -> None:
        self.tags: dict[str, str] = {}

    def set_tag(self, key: str, value: str) -> None:
        self.tags[key] = value


class _FakePushScope:
    def __init__(self, scope: _FakeScope) -> None:
        self.scope = scope

    def __enter__(self) -> _FakeScope:
        return self.scope

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None


def test_trace_context_returns_none_for_invalid_span(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(error_tracking_module.trace, "get_current_span", lambda: _FakeSpan(valid=False))

    assert error_tracking_module._trace_context() == (None, None)


def test_scrub_event_payload_redacts_sensitive_request_data() -> None:
    event = {
        "request": {
            "headers": {
                "Authorization": "Bearer secret",
                "Cookie": "cookie=value",
                "Set-Cookie": "session=1",
                "X-Test": "ok",
            },
            "data": {"secret": "value"},
        }
    }

    scrubbed = error_tracking_module._scrub_event_payload(event)

    assert scrubbed["request"]["headers"]["Authorization"] == "[REDACTED]"
    assert scrubbed["request"]["headers"]["Cookie"] == "[REDACTED]"
    assert scrubbed["request"]["headers"]["Set-Cookie"] == "[REDACTED]"
    assert scrubbed["request"]["headers"]["X-Test"] == "ok"
    assert scrubbed["request"]["data"] == "[FILTERED]"


def test_before_send_enriches_event_with_context_and_trace(monkeypatch: pytest.MonkeyPatch) -> None:
    request_token = set_request_id("request-1")
    correlation_token = set_correlation_id("correlation-1")
    monkeypatch.setattr(error_tracking_module.trace, "get_current_span", lambda: _FakeSpan(valid=True))

    try:
        event = error_tracking_module._before_send({"request": {"headers": {}, "data": "secret"}}, {})
    finally:
        reset_correlation_id(correlation_token)
        reset_request_id(request_token)

    assert event is not None
    assert event["tags"] == {
        "request_id": "request-1",
        "correlation_id": "correlation-1",
        "trace_id": "11111111111111111111111111111111",
        "span_id": "2222222222222222",
    }
    assert event["extra"] == {
        "request_id": "request-1",
        "correlation_id": "correlation-1",
        "trace_id": "11111111111111111111111111111111",
        "span_id": "2222222222222222",
    }


def test_setup_error_tracking_obeys_feature_flags_and_initializes_once(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []
    settings = build_settings(
        observability={
            "enabled": True,
            "sentry_enabled": True,
            "glitchtip_dsn": "https://glitchtip.example/1",
            "profile_sample_rate": 0.5,
        }
    )

    monkeypatch.setattr(error_tracking_module, "_SENTRY_CONFIGURED", False)
    monkeypatch.setattr(error_tracking_module.sentry_sdk, "init", lambda **kwargs: calls.append(kwargs))

    error_tracking_module.setup_error_tracking(build_settings(observability={"enabled": False}))
    error_tracking_module.setup_error_tracking(build_settings(observability={"sentry_enabled": True}))
    error_tracking_module.setup_error_tracking(settings)
    error_tracking_module.setup_error_tracking(settings)

    assert len(calls) == 1
    assert calls[0]["dsn"] == "https://glitchtip.example/1"
    assert calls[0]["before_send"] is error_tracking_module._before_send


def test_capture_handled_exception_and_flush_use_sentry_when_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    request = SimpleNamespace(url=SimpleNamespace(path="/boom"), method="POST")
    exc = RuntimeError("boom")
    scope = _FakeScope()
    captured: dict[str, object] = {}
    request_token = set_request_id("request-2")
    correlation_token = set_correlation_id("correlation-2")

    monkeypatch.setattr(error_tracking_module, "_SENTRY_CONFIGURED", True)
    monkeypatch.setattr(error_tracking_module.trace, "get_current_span", lambda: _FakeSpan(valid=True))
    monkeypatch.setattr(error_tracking_module.sentry_sdk, "push_scope", lambda: _FakePushScope(scope))
    monkeypatch.setattr(
        error_tracking_module.sentry_sdk,
        "capture_exception",
        lambda received_exc: captured.setdefault("exception", received_exc),
    )
    monkeypatch.setattr(
        error_tracking_module.sentry_sdk,
        "flush",
        lambda *, timeout: captured.setdefault("flush_timeout", timeout),
    )

    try:
        error_tracking_module.capture_handled_exception(request, exc)
    finally:
        reset_correlation_id(correlation_token)
        reset_request_id(request_token)

    monkeypatch.setattr(error_tracking_module, "_SENTRY_CONFIGURED", False)
    error_tracking_module.capture_handled_exception(request, exc)
    monkeypatch.setattr(error_tracking_module, "_SENTRY_CONFIGURED", True)
    error_tracking_module.flush_error_tracking()

    assert captured["exception"] is exc
    assert captured["flush_timeout"] == 2.0
    assert scope.tags == {
        "http.path": "/boom",
        "http.method": "POST",
        "request_id": "request-2",
        "correlation_id": "correlation-2",
        "trace_id": "11111111111111111111111111111111",
        "span_id": "2222222222222222",
    }
