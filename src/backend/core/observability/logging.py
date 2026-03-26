import json
import logging
import logging.config
from collections.abc import MutableMapping
from dataclasses import dataclass
from typing import Any

import structlog
from opentelemetry import trace

from core.observability.context import get_correlation_id, get_request_id
from core.settings import Settings


@dataclass(slots=True)
class _LoggingRuntime:
    service_name: str
    environment: str


_LOGGING_RUNTIME = _LoggingRuntime(service_name="unknown-service", environment="unknown-environment")
_LOGGING_CONFIGURED = False


def _redact_sensitive_values(
    logger: Any,
    method_name: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    del logger, method_name
    sensitive_keys = {
        "access_token",
        "api_key",
        "apikey",
        "authorization",
        "bearer",
        "cookie",
        "jwt",
        "password",
        "refresh_token",
        "secret",
        "session",
        "session_id",
        "set-cookie",
        "token",
        "x-api-key",
    }
    for key, value in tuple(event_dict.items()):
        if key.lower() in sensitive_keys and value is not None:
            event_dict[key] = "[REDACTED]"
    return event_dict


def _enrich_observability_context(
    logger: Any,
    method_name: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    del logger, method_name
    event_dict["service"] = _LOGGING_RUNTIME.service_name
    event_dict["environment"] = _LOGGING_RUNTIME.environment
    request_id = get_request_id()
    if request_id is not None:
        event_dict["request_id"] = request_id
    correlation_id = get_correlation_id()
    if correlation_id is not None:
        event_dict["correlation_id"] = correlation_id

    span = trace.get_current_span()
    span_context = span.get_span_context()
    if span_context.is_valid:
        event_dict["trace_id"] = f"{span_context.trace_id:032x}"
        event_dict["span_id"] = f"{span_context.span_id:016x}"

    event = event_dict.get("event")
    if isinstance(event, str):
        event_dict["message"] = event
    return event_dict


def _shared_processors() -> list[structlog.types.Processor]:
    return [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _redact_sensitive_values,
        _enrich_observability_context,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]


def setup_logging(settings: Settings) -> None:
    """Configure structured JSON logging for application and library loggers."""
    global _LOGGING_CONFIGURED

    _LOGGING_RUNTIME.service_name = settings.observability_service_name
    _LOGGING_RUNTIME.environment = settings.observability_environment
    if not settings.observability.enabled or not settings.observability.logs_enabled:
        return
    if _LOGGING_CONFIGURED:
        return

    shared_processors = _shared_processors()
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "foreign_pre_chain": shared_processors,
                    "processor": structlog.processors.JSONRenderer(serializer=json.dumps, sort_keys=True),
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                }
            },
            "root": {
                "handlers": ["default"],
                "level": settings.observability.log_level,
            },
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": settings.observability.log_level, "propagate": False},
                "uvicorn.error": {
                    "handlers": ["default"],
                    "level": settings.observability.log_level,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["default"],
                    "level": settings.observability.log_level,
                    "propagate": False,
                },
            },
        }
    )
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    _LOGGING_CONFIGURED = True


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return the project-standard structured logger."""
    return structlog.stdlib.get_logger(name)
