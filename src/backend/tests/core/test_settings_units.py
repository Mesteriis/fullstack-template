import pytest
from core.settings.base import ApiSettings, AppSettings, ObservabilitySettings, Settings, SystemSettings, get_settings
from tests.helpers import build_settings


def test_api_and_observability_settings_normalize_input() -> None:
    api = ApiSettings(prefix="internal")
    observability = ObservabilitySettings(
        metrics_path="metrics",
        request_id_header=" X-Request-ID ",
        correlation_id_header=" X-Correlation-ID ",
        log_level="debug",
    )

    assert api.prefix == "/internal"
    assert observability.metrics_path == "/metrics"
    assert observability.request_id_header == "X-Request-ID"
    assert observability.correlation_id_header == "X-Correlation-ID"
    assert observability.log_level == "DEBUG"


def test_observability_settings_validate_required_values() -> None:
    with pytest.raises(ValueError):
        ObservabilitySettings(request_id_header=" ")

    with pytest.raises(ValueError):
        ObservabilitySettings(trace_sample_rate=1.1)

    with pytest.raises(ValueError):
        SystemSettings(health_timeout_seconds=0)


def test_settings_observability_properties_fall_back_to_app_values() -> None:
    default = build_settings(app={"name": "Platform API", "version": "2.1.0", "environment": "staging"})
    explicit = build_settings(
        app={"name": "Platform API", "version": "2.1.0", "environment": "staging"},
        observability={
            "service_name": "obs-service",
            "service_version": "2026.03",
            "environment": "production",
        },
    )

    assert default.observability_service_name == "Platform API"
    assert default.observability_service_version == "2.1.0"
    assert default.observability_environment == "staging"
    assert explicit.observability_service_name == "obs-service"
    assert explicit.observability_service_version == "2026.03"
    assert explicit.observability_environment == "production"


def test_settings_sections_only_consume_their_own_prefixes(monkeypatch: pytest.MonkeyPatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP__NAME", "Scoped App")
    monkeypatch.setenv("API__NAME", "wrong-section")
    monkeypatch.setenv("API__PREFIX", "internal")
    monkeypatch.setenv("SYSTEM__HEALTH_TIMEOUT_SECONDS", "2.5")
    monkeypatch.setenv("OBSERVABILITY__LOG_LEVEL", "debug")

    app = AppSettings()
    api = ApiSettings()
    system = SystemSettings()
    observability = ObservabilitySettings()

    assert app.name == "Scoped App"
    assert app.name != "wrong-section"
    assert api.prefix == "/internal"
    assert system.health_timeout_seconds == 2.5
    assert observability.log_level == "DEBUG"

    get_settings.cache_clear()


def test_get_settings_is_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("API__PREFIX", "cached")

    first = get_settings()
    second = get_settings()

    assert type(first).__name__ == Settings.__name__
    assert first is second
    assert first.api.prefix == "/cached"

    get_settings.cache_clear()
