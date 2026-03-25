from collections.abc import Callable

from fastapi.testclient import TestClient


def test_request_id_is_generated_for_incoming_requests(
    client: TestClient,
    reverse: Callable[[str], str],
) -> None:
    response = client.get(reverse("read_liveness"))

    assert response.status_code == 200
    assert response.headers["x-request-id"]
    assert response.headers["x-correlation-id"] == response.headers["x-request-id"]


def test_request_id_from_client_is_preserved(
    client: TestClient,
    reverse: Callable[[str], str],
) -> None:
    response = client.get(reverse("read_liveness"), headers={"X-Request-ID": "request-from-client"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "request-from-client"
    assert response.headers["x-correlation-id"] == "request-from-client"


def test_correlation_id_from_client_is_preserved(
    client: TestClient,
    reverse: Callable[[str], str],
) -> None:
    response = client.get(
        reverse("read_liveness"),
        headers={
            "X-Request-ID": "request-from-client",
            "X-Correlation-ID": "correlation-from-client",
        },
    )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "request-from-client"
    assert response.headers["x-correlation-id"] == "correlation-from-client"


def test_metrics_endpoint_is_exposed(client: TestClient, settings: object) -> None:
    response = client.get(settings.observability.metrics_path)

    assert response.status_code == 200
    assert "http_requests_total" in response.text
