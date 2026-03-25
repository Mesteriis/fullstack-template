import importlib.util
from pathlib import Path

from core.http.errors import ApiError


def _errors_module():
    module_path = Path(__file__).resolve().parents[3] / "apps" / "system" / "api" / "errors.py"
    spec = importlib.util.spec_from_file_location("tests.apps.system.api_errors", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_system_error_responses_describe_registered_error_payloads() -> None:
    responses = _errors_module().system_error_responses(404, 500)

    assert responses == {
        404: {"model": ApiError, "description": "Requested system resource was not found."},
        500: {"model": ApiError, "description": "Unexpected system error."},
    }


def test_system_resource_not_found_error_builds_http_exception_payload() -> None:
    error = _errors_module().system_resource_not_found_error(resource="health probe")

    assert error.status_code == 404
    assert error.detail["code"] == "resource_not_found"
    assert error.detail["message"] == "Requested health probe was not found."
