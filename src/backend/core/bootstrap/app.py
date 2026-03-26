from apps.system.contracts import ServiceMetadata
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from api import api_router
from core.bootstrap.system import close_system_redis_clients
from core.errors import PlatformError
from core.http.handlers import handle_platform_error, handle_request_validation_error, handle_unexpected_error
from core.observability import setup_observability
from core.settings import Settings, get_settings


def _is_local_environment(environment: str) -> bool:
    return environment.strip().lower() in {"local", "dev", "development"}


def create_app(*, settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI application from an explicit settings-owned bootstrap path."""
    runtime_settings = settings or get_settings()
    app = FastAPI(title=runtime_settings.app.name)
    if _is_local_environment(runtime_settings.app.environment):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    setup_observability(app, runtime_settings)
    app.add_exception_handler(PlatformError, handle_platform_error)
    app.add_exception_handler(RequestValidationError, handle_request_validation_error)
    app.add_exception_handler(Exception, handle_unexpected_error)
    app.include_router(api_router, prefix=runtime_settings.api.prefix)
    app.add_event_handler("shutdown", close_system_redis_clients)

    @app.get("/", tags=["meta"], response_model=ServiceMetadata)
    async def read_root() -> ServiceMetadata:
        return ServiceMetadata(
            service=runtime_settings.app.name,
            docs="/docs",
            health=f"{runtime_settings.api.prefix}/v1/system/health",
            liveness=f"{runtime_settings.api.prefix}/v1/system/livez",
            readiness=f"{runtime_settings.api.prefix}/v1/system/readyz",
        )

    return app
