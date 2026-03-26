from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio

from core.db import get_async_engine
from core.settings import Settings

_FASTAPI_INSTRUMENTED_APPS: set[int] = set()
_TRACING_PROVIDER_CONFIGURED = False
_SQLALCHEMY_INSTRUMENTED = False
_REDIS_INSTRUMENTED = False


def _parse_otlp_headers(raw_headers: str) -> dict[str, str]:
    headers: dict[str, str] = {}
    if not raw_headers.strip():
        return headers

    for item in raw_headers.split(","):
        entry = item.strip()
        if not entry:
            continue
        key, separator, value = entry.partition("=")
        if not separator or not key.strip() or not value.strip():
            msg = f"invalid OTLP header entry '{entry}', expected KEY=VALUE"
            raise ValueError(msg)
        headers[key.strip()] = value.strip()
    return headers


def _resource_attributes(settings: Settings) -> dict[str, str]:
    return {
        "service.name": settings.observability_service_name,
        "service.version": settings.observability_service_version,
        "deployment.environment": settings.observability_environment,
    }


def _ensure_tracer_provider(settings: Settings) -> TracerProvider:
    global _TRACING_PROVIDER_CONFIGURED

    existing_provider = trace.get_tracer_provider()
    if isinstance(existing_provider, TracerProvider):
        return existing_provider

    provider = TracerProvider(
        resource=Resource.create(_resource_attributes(settings)),
        sampler=ParentBasedTraceIdRatio(settings.observability.trace_sample_rate),
    )
    provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=settings.observability.otlp_endpoint,
                headers=_parse_otlp_headers(settings.observability.otlp_headers),
            )
        )
    )
    if not _TRACING_PROVIDER_CONFIGURED:
        trace.set_tracer_provider(provider)
        _TRACING_PROVIDER_CONFIGURED = True
    return trace.get_tracer_provider()  # type: ignore[return-value]


def setup_tracing(app: FastAPI, settings: Settings) -> None:
    """Configure OpenTelemetry tracing and supported client instrumentations."""
    global _SQLALCHEMY_INSTRUMENTED, _REDIS_INSTRUMENTED

    if not settings.observability.enabled or not settings.observability.traces_enabled:
        return
    if not settings.observability.otlp_endpoint:
        return

    tracer_provider = _ensure_tracer_provider(settings)
    app_key = id(app)
    if app_key not in _FASTAPI_INSTRUMENTED_APPS:
        FastAPIInstrumentor.instrument_app(
            app,
            tracer_provider=tracer_provider,
            excluded_urls=settings.observability.metrics_path,
        )
        _FASTAPI_INSTRUMENTED_APPS.add(app_key)

    if settings.observability.instrument_sqlalchemy and not _SQLALCHEMY_INSTRUMENTED:
        SQLAlchemyInstrumentor().instrument(engine=get_async_engine().sync_engine)
        _SQLALCHEMY_INSTRUMENTED = True

    if settings.observability.instrument_redis and not _REDIS_INSTRUMENTED:
        RedisInstrumentor().instrument()
        _REDIS_INSTRUMENTED = True

    if not getattr(app.state, "tracing_flush_registered", False):
        app.add_event_handler("shutdown", flush_tracing)
        app.state.tracing_flush_registered = True


def flush_tracing() -> None:
    """Flush spans during graceful application shutdown."""
    provider = trace.get_tracer_provider()
    force_flush = getattr(provider, "force_flush", None)
    if callable(force_flush):
        force_flush()
