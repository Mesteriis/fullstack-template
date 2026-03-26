from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[4] / ".env"


def _section_settings_config(prefix: str) -> SettingsConfigDict:
    return SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        env_prefix=prefix,
        extra="ignore",
    )


class AppSettings(BaseSettings):
    """Application metadata settings sourced from the `APP__*` env namespace."""

    model_config = _section_settings_config("APP__")

    name: str = "Fullstack Template API"
    version: str = "0.1.0"
    environment: str = "local"


class ApiSettings(BaseSettings):
    """HTTP server settings sourced from the `API__*` env namespace."""

    model_config = _section_settings_config("API__")

    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    prefix: str = "/api"

    @field_validator("prefix")
    @classmethod
    def normalize_prefix(cls, value: str) -> str:
        return value if value.startswith("/") else f"/{value}"


class DatabaseSettings(BaseSettings):
    """Database/cache settings sourced from the `DB__*` env namespace."""

    model_config = _section_settings_config("DB__")

    postgres_dsn: str = "postgresql+asyncpg://fullstack_template:fullstack_template@localhost:5432/fullstack_template"
    redis_url: str = "redis://localhost:6379/0"


class BrokerSettings(BaseSettings):
    """Background broker settings sourced from the `BROKER__*` env namespace."""

    model_config = _section_settings_config("BROKER__")

    taskiq_queue_name: str = "fullstack-template:taskiq"
    taskiq_consumer_group_name: str = "fullstack-template:backend"


class SystemSettings(BaseSettings):
    """System bounded-context settings sourced from the `SYSTEM__*` env namespace."""

    model_config = _section_settings_config("SYSTEM__")

    health_timeout_seconds: float = 5.0

    @field_validator("health_timeout_seconds")
    @classmethod
    def validate_health_timeout_seconds(cls, value: float) -> float:
        if value <= 0:
            msg = "system health timeout must be greater than 0 seconds"
            raise ValueError(msg)
        return value


class ObservabilitySettings(BaseSettings):
    """Observability settings sourced from the `OBSERVABILITY__*` env namespace."""

    model_config = _section_settings_config("OBSERVABILITY__")

    enabled: bool = True
    logs_enabled: bool = True
    log_level: str = "INFO"
    traces_enabled: bool = False
    otlp_endpoint: str = ""
    otlp_headers: str = ""
    metrics_enabled: bool = True
    metrics_path: str = "/metrics"
    request_id_header: str = "X-Request-ID"
    correlation_id_header: str = "X-Correlation-ID"
    sentry_enabled: bool = False
    glitchtip_dsn: str = ""
    trace_sample_rate: float = 0.1
    profile_sample_rate: float = 0.0
    instrument_sqlalchemy: bool = True
    instrument_redis: bool = True
    instrument_httpx: bool = False
    service_name: str | None = None
    service_version: str | None = None
    environment: str | None = None

    @field_validator("metrics_path")
    @classmethod
    def normalize_metrics_path(cls, value: str) -> str:
        return value if value.startswith("/") else f"/{value}"

    @field_validator("request_id_header", "correlation_id_header")
    @classmethod
    def normalize_context_header(cls, value: str) -> str:
        header_name = value.strip()
        if not header_name:
            msg = "observability context header names must not be empty"
            raise ValueError(msg)
        return header_name

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("trace_sample_rate", "profile_sample_rate")
    @classmethod
    def validate_sample_rate(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            msg = "observability sample rates must be between 0.0 and 1.0"
            raise ValueError(msg)
        return value


class Settings(BaseSettings):
    """Aggregate backend settings.

    Each nested section is an independent `BaseSettings` model that reads the
    repository `.env` file and only consumes its own prefixed namespace.
    """

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app: AppSettings = Field(default_factory=AppSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    broker: BrokerSettings = Field(default_factory=BrokerSettings)
    system: SystemSettings = Field(default_factory=SystemSettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)

    @property
    def observability_service_name(self) -> str:
        return self.observability.service_name or self.app.name

    @property
    def observability_service_version(self) -> str:
        return self.observability.service_version or self.app.version

    @property
    def observability_environment(self) -> str:
        return self.observability.environment or self.app.environment


@lru_cache
def get_settings() -> Settings:
    return Settings()
