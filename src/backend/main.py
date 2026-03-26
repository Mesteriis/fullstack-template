import uvicorn
from core.bootstrap import create_app
from core.observability import setup_logging
from core.settings import Settings, get_settings
from fastapi import FastAPI


def bootstrap_runtime() -> tuple[Settings, FastAPI]:
    """Create the runtime settings/app pair used by the ASGI entrypoint.

    The module still exposes a top-level ``app`` for ASGI servers, but all
    bootstrap work is centralized here so tests and runtime composition use the
    same explicit path.
    """

    runtime_settings = get_settings()
    setup_logging(runtime_settings)
    runtime_app = create_app(settings=runtime_settings)
    return runtime_settings, runtime_app


settings, app = bootstrap_runtime()


def run() -> None:
    uvicorn.run(
        "main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.reload,
        log_config=None,
    )


if __name__ == "__main__":
    run()
