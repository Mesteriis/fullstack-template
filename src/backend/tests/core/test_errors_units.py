import pytest
from core.errors import (
    DuplicateMessageKeyError,
    DuplicateRequestError,
    ErrorCategory,
    ErrorDefinition,
    ErrorDomain,
    ErrorRegistry,
    ErrorSeverity,
    IntegrationUnreachableError,
    PlatformError,
    ResourceNotFoundError,
    UnknownErrorCodeError,
    UnknownMessageKeyError,
    ValidationFailedError,
)


def _definition(
    *,
    error_code: str = "test_error",
    message_key: str = "error.test",
    default_message: str = "Failure for {resource}.",
) -> ErrorDefinition:
    return ErrorDefinition(
        error_code=error_code,
        message_key=message_key,
        default_message=default_message,
        domain=ErrorDomain.CORE,
        category=ErrorCategory.INTERNAL,
        http_status=500,
        severity=ErrorSeverity.ERROR,
        retryable=True,
        safe_to_expose=False,
    )


def test_error_definition_renders_values_and_falls_back_for_missing_params() -> None:
    definition = _definition()

    assert definition.render_message({"resource": "queue"}) == "Failure for queue."
    assert definition.render_message() == "Failure for {resource}."


def test_error_registry_supports_register_lookup_contains_and_iteration() -> None:
    first = _definition(error_code="first", message_key="error.first")
    second = _definition(error_code="second", message_key="error.second")
    registry = ErrorRegistry((first,))

    assert registry.register(second) is second
    assert registry.get("first") is first
    assert registry.get_by_message_key("error.second") is second
    assert "first" in registry
    assert "missing" not in registry
    assert [definition.error_code for definition in registry] == ["first", "second"]


def test_error_registry_rejects_duplicate_message_keys_and_unknown_values() -> None:
    registry = ErrorRegistry((_definition(error_code="first", message_key="error.shared"),))

    with pytest.raises(DuplicateMessageKeyError):
        registry.register(_definition(error_code="second", message_key="error.shared"))

    with pytest.raises(UnknownErrorCodeError):
        registry.get("missing")

    with pytest.raises(UnknownMessageKeyError):
        registry.get_by_message_key("missing.key")


def test_platform_error_exposes_metadata_and_registry_backed_errors() -> None:
    error = PlatformError(
        _definition(),
        params={"resource": "cache"},
        details={"component": "worker"},
        retryable=False,
    )
    not_found = ResourceNotFoundError(resource="health probe", details={"source": "api"})
    validation = ValidationFailedError()
    duplicate = DuplicateRequestError()
    integration = IntegrationUnreachableError(
        integration="redis",
        details={"target": "cache"},
        retryable=False,
    )

    assert error.to_metadata() == {
        "error_code": "test_error",
        "message_key": "error.test",
        "domain": "core",
        "category": "internal",
        "http_status": 500,
        "severity": "error",
        "retryable": False,
        "safe_to_expose": False,
        "params": {"resource": "cache"},
        "details": {"component": "worker"},
    }
    assert not_found.message == "Requested health probe was not found."
    assert not_found.details == {"source": "api"}
    assert validation.http_status == 400
    assert duplicate.http_status == 409
    assert integration.message == "Integration 'redis' is unavailable."
    assert integration.retryable is False
