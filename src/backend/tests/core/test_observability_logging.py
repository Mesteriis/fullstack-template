from types import SimpleNamespace
from typing import Any, cast

import pytest
from core.observability import logging as observability_logging_module
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
        self.trace_id = int("a" * 32, 16)
        self.span_id = int("b" * 16, 16)


class _FakeSpan:
    def __init__(self, *, valid: bool) -> None:
        self._span_context = _FakeSpanContext(valid=valid)

    def get_span_context(self) -> _FakeSpanContext:
        return self._span_context


def test_redact_sensitive_values_masks_known_secret_fields() -> None:
    event = {
        "Authorization": "Bearer secret",
        "api_key": "api-key",
        "x-api-key": "x-key",
        "access_token": "access",
        "cookie": "session=1",
        "session_id": "session-id",
        "jwt": "jwt-token",
        "bearer": "bearer-token",
        "token": "abc",
        "safe": "value",
    }

    redacted = observability_logging_module._redact_sensitive_values(None, "info", event)

    assert redacted == {
        "Authorization": "[REDACTED]",
        "api_key": "[REDACTED]",
        "x-api-key": "[REDACTED]",
        "access_token": "[REDACTED]",
        "cookie": "[REDACTED]",
        "session_id": "[REDACTED]",
        "jwt": "[REDACTED]",
        "bearer": "[REDACTED]",
        "token": "[REDACTED]",
        "safe": "value",
    }


def test_enrich_observability_context_adds_runtime_context_and_trace(monkeypatch: pytest.MonkeyPatch) -> None:
    request_token = set_request_id("request-1")
    correlation_token = set_correlation_id("correlation-1")
    monkeypatch.setattr(
        cast(Any, observability_logging_module).trace, "get_current_span", lambda: _FakeSpan(valid=True)
    )
    observability_logging_module._LOGGING_RUNTIME.service_name = "Platform API"
    observability_logging_module._LOGGING_RUNTIME.environment = "test"

    try:
        event = observability_logging_module._enrich_observability_context(None, "info", {"event": "processed"})
    finally:
        reset_correlation_id(correlation_token)
        reset_request_id(request_token)

    assert event["service"] == "Platform API"
    assert event["environment"] == "test"
    assert event["request_id"] == "request-1"
    assert event["correlation_id"] == "correlation-1"
    assert event["trace_id"] == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    assert event["span_id"] == "bbbbbbbbbbbbbbbb"
    assert event["message"] == "processed"


def test_shared_processors_include_redaction_and_context_enrichment() -> None:
    processors = observability_logging_module._shared_processors()

    assert observability_logging_module._redact_sensitive_values in processors
    assert observability_logging_module._enrich_observability_context in processors


def test_setup_logging_skips_when_disabled_and_configures_once(monkeypatch: pytest.MonkeyPatch) -> None:
    disabled_settings = build_settings(observability={"enabled": False})
    enabled_settings = build_settings(
        app={"name": "Platform API", "environment": "test"},
        observability={"enabled": True, "logs_enabled": True, "log_level": "WARNING"},
    )
    calls: list[str] = []

    monkeypatch.setattr(observability_logging_module, "_LOGGING_CONFIGURED", False)
    monkeypatch.setattr(
        cast(Any, observability_logging_module).logging.config, "dictConfig", lambda config: calls.append("dict")
    )
    monkeypatch.setattr(
        cast(Any, observability_logging_module).structlog, "configure", lambda **kwargs: calls.append("structlog")
    )

    observability_logging_module.setup_logging(disabled_settings)
    observability_logging_module.setup_logging(enabled_settings)
    observability_logging_module.setup_logging(enabled_settings)

    assert calls == ["dict", "structlog"]
    assert observability_logging_module._LOGGING_RUNTIME.service_name == "Platform API"
    assert observability_logging_module._LOGGING_RUNTIME.environment == "test"


def test_get_logger_uses_structlog_factory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cast(Any, observability_logging_module).structlog.stdlib,
        "get_logger",
        lambda name: SimpleNamespace(name=name),
    )

    logger = observability_logging_module.get_logger("tests.logger")

    assert logger.name == "tests.logger"
