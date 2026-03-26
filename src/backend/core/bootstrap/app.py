from apps.system.contracts import ServiceMetadata
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from api import api_router
from core.errors import PlatformError
from core.http.handlers import handle_platform_error, handle_request_validation_error, handle_unexpected_error
from core.observability import setup_observability
from core.settings import get_settings


def _is_local_environment(environment: str) -> bool:
    return environment.strip().lower() in {"local", "dev", "development"}


def create_app() -> FastAPI:
    """Build the FastAPI application from the settings-owned bootstrap path."""
    settings = get_settings()
    app = FastAPI(title=settings.app.name)
    if _is_local_environment(settings.app.environment):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    setup_observability(app, settings)
    app.add_exception_handler(PlatformError, handle_platform_error)
    app.add_exception_handler(RequestValidationError, handle_request_validation_error)
    app.add_exception_handler(Exception, handle_unexpected_error)
    app.include_router(api_router, prefix=settings.api.prefix)

    @app.get("/", tags=["meta"], response_model=ServiceMetadata)
    async def read_root() -> ServiceMetadata:
        return ServiceMetadata(
            service=settings.app.name,
            docs="/docs",
            health=f"{settings.api.prefix}/v1/system/health",
            liveness=f"{settings.api.prefix}/v1/system/livez",
            readiness=f"{settings.api.prefix}/v1/system/readyz",
        )

    return app
