from typing import Any, cast

import pytest
from core.bootstrap import app as bootstrap_app_module
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from tests.helpers import build_settings


def test_create_app_enables_local_cors_for_dev_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bootstrap_app_module, "setup_observability", lambda app, settings: None)
    monkeypatch.setattr(bootstrap_app_module, "get_settings", lambda: build_settings(app={"environment": "local"}))

    app = bootstrap_app_module.create_app()
    cors_middlewares = [middleware for middleware in app.user_middleware if cast(Any, middleware).cls is CORSMiddleware]

    assert len(cors_middlewares) == 1
    middleware: Middleware = cors_middlewares[0]
    assert middleware.kwargs["allow_origins"] == ["http://localhost:5173"]


def test_create_app_does_not_enable_cors_outside_local_dev(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bootstrap_app_module, "setup_observability", lambda app, settings: None)
    monkeypatch.setattr(bootstrap_app_module, "get_settings", lambda: build_settings(app={"environment": "production"}))

    app = bootstrap_app_module.create_app()

    assert all(cast(Any, middleware).cls is not CORSMiddleware for middleware in app.user_middleware)
