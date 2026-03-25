from collections.abc import Callable

import pytest
from core.errors import (
    DuplicateErrorCodeError,
    ErrorCategory,
    ErrorDefinition,
    ErrorDomain,
    ErrorRegistry,
    ErrorSeverity,
    ResourceNotFoundError,
)
from core.http.errors import ApiError
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient
from tests.factories import ApiErrorDetailFactory, ApiErrorFactory


def test_error_registry_rejects_duplicate_error_codes() -> None:
    registry = ErrorRegistry(
        definitions=(
            ErrorDefinition(
                error_code="test_error",
                message_key="error.test.one",
                default_message="Test error.",
                domain=ErrorDomain.CORE,
                category=ErrorCategory.INTERNAL,
                http_status=500,
                severity=ErrorSeverity.ERROR,
            ),
        )
    )

    with pytest.raises(DuplicateErrorCodeError):
        registry.register(
            ErrorDefinition(
                error_code="test_error",
                message_key="error.test.two",
                default_message="Another test error.",
                domain=ErrorDomain.CORE,
                category=ErrorCategory.INTERNAL,
                http_status=500,
                severity=ErrorSeverity.ERROR,
            )
        )


def test_platform_error_handler_returns_structured_payload(
    app_factory: Callable[..., FastAPI],
    faker: Faker,
) -> None:
    app = app_factory()
    correlation_id = faker.uuid4()

    @app.get("/test-errors/not-found", name="test_platform_error")
    async def read_missing() -> None:
        raise ResourceNotFoundError(resource="system probe")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(app.url_path_for("test_platform_error"), headers={"X-Correlation-ID": correlation_id})

    payload = ApiError.model_validate(response.json())

    assert response.status_code == 404
    assert response.headers["x-correlation-id"] == correlation_id
    assert payload == ApiErrorFactory.build(
        code="resource_not_found",
        message="Requested system probe was not found.",
        message_key="error.resource.not_found",
        domain="api",
        category="not_found",
        http_status=404,
        severity="warning",
        safe_to_expose=True,
        details=(),
        retryable=False,
        request_id=response.headers["x-request-id"],
        correlation_id=correlation_id,
    )


def test_request_validation_handler_returns_structured_payload(
    app_factory: Callable[..., FastAPI],
    faker: Faker,
) -> None:
    app = app_factory()
    request_id = faker.uuid4()

    @app.get("/test-errors/validation", name="test_validation_error")
    async def read_validation(limit: int) -> dict[str, int]:
        return {"limit": limit}

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(
            app.url_path_for("test_validation_error"),
            params={"limit": "bad"},
            headers={"X-Request-ID": request_id},
        )

    payload = ApiError.model_validate(response.json())

    assert response.status_code == 400
    assert response.headers["x-request-id"] == request_id
    assert payload == ApiErrorFactory.build(
        code="validation_failed",
        message="Request validation failed.",
        message_key="error.request.validation_failed",
        domain="api",
        category="validation",
        http_status=400,
        severity="warning",
        safe_to_expose=True,
        details=(
            ApiErrorDetailFactory.build(
                field="query.limit",
                message="Input should be a valid integer, unable to parse string as an integer",
                value="bad",
            ),
        ),
        retryable=False,
        request_id=request_id,
        correlation_id=request_id,
    )


def test_unhandled_error_handler_returns_internal_payload(
    app_factory: Callable[..., FastAPI],
    faker: Faker,
) -> None:
    app = app_factory()
    correlation_id = faker.uuid4()

    @app.get("/test-errors/unhandled", name="test_unhandled_error")
    async def read_unhandled() -> None:
        raise RuntimeError("boom")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(app.url_path_for("test_unhandled_error"), headers={"X-Correlation-ID": correlation_id})

    payload = ApiError.model_validate(response.json())

    assert response.status_code == 500
    assert response.headers["x-correlation-id"] == correlation_id
    assert payload == ApiErrorFactory.build(
        code="internal_error",
        message="Internal server error.",
        message_key="error.system.internal",
        domain="core",
        category="internal",
        http_status=500,
        severity="error",
        safe_to_expose=False,
        details=(),
        retryable=False,
        request_id=response.headers["x-request-id"],
        correlation_id=correlation_id,
    )
