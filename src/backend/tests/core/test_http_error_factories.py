from core.errors import ResourceNotFoundError
from core.http.errors import ApiError, ApiErrorDetail, ApiErrorFactory


def test_api_error_factory_builds_detail_payloads_and_http_exception() -> None:
    detail = ApiErrorFactory.build_detail(field="query.limit", message="must be integer", value="bad")
    error = ResourceNotFoundError(resource="system probe")

    payload = ApiErrorFactory.build(
        code="validation_failed",
        message="Request validation failed.",
        details=(detail,),
        request_id="request-1",
        correlation_id="correlation-1",
    )
    platform_payload = ApiErrorFactory.build_from_platform_error(
        error,
        details=(detail,),
        request_id="request-2",
        correlation_id="correlation-2",
    )
    http_error = ApiErrorFactory.from_platform_error(
        error,
        details=(detail,),
        request_id="request-2",
        correlation_id="correlation-2",
        headers={"X-Test": "true"},
    )

    assert detail == ApiErrorDetail(field="query.limit", message="must be integer", value="bad")
    assert payload == ApiError(
        code="validation_failed",
        message="Request validation failed.",
        details=(detail,),
        request_id="request-1",
        correlation_id="correlation-1",
    )
    assert platform_payload.code == "resource_not_found"
    assert platform_payload.details == (detail,)
    assert http_error.status_code == 404
    assert http_error.detail["message"] == "Requested system probe was not found."
    assert http_error.detail["request_id"] == "request-2"
    assert http_error.headers == {"X-Test": "true"}
