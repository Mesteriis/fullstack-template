from collections.abc import Callable

from apps.system.contracts.health import LivenessProbe, ReadinessProbe
from apps.system.contracts.meta import ServiceMetadata
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient
from tests.factories import (
    DependencyProbeFactory,
    LivenessProbeFactory,
    ReadinessProbeFactory,
    ServiceMetadataFactory,
)


def test_root_returns_service_metadata(
    client: TestClient,
    reverse: Callable[[str], str],
) -> None:
    response = client.get(reverse("read_root"))
    payload = ServiceMetadata.model_validate(response.json())

    assert response.status_code == 200
    expected = ServiceMetadataFactory.build(
        service="Registries API",
        docs="/docs",
        health=reverse("read_health"),
        liveness=reverse("read_liveness"),
        readiness=reverse("read_readiness"),
    )
    assert payload == expected


def test_liveness_endpoint_returns_ok_status(
    client: TestClient,
    reverse: Callable[[str], str],
) -> None:
    response = client.get(reverse("read_liveness"))
    payload = LivenessProbe.model_validate(response.json())

    assert response.status_code == 200
    assert payload == LivenessProbeFactory.build(service="Registries API")


def test_readiness_endpoint_returns_dependency_statuses(
    client: TestClient,
    reverse: Callable[[str], str],
) -> None:
    response = client.get(reverse("read_readiness"))
    payload = ReadinessProbe.model_validate(response.json())

    assert response.status_code == 200
    assert payload == ReadinessProbeFactory.build(
        status="ok",
        service="Registries API",
        checks=(
            DependencyProbeFactory.build(name="postgres", status="ok", detail=None),
            DependencyProbeFactory.build(name="redis", status="ok", detail=None),
        ),
    )


def test_health_endpoint_returns_dependency_statuses(
    client: TestClient,
    reverse: Callable[[str], str],
) -> None:
    response = client.get(reverse("read_health"))
    payload = ReadinessProbe.model_validate(response.json())

    assert response.status_code == 200
    assert payload == ReadinessProbeFactory.build(
        status="ok",
        service="Registries API",
        checks=(
            DependencyProbeFactory.build(name="postgres", status="ok", detail=None),
            DependencyProbeFactory.build(name="redis", status="ok", detail=None),
        ),
    )


def test_readiness_returns_503_when_redis_is_unreachable(
    app_factory: Callable[..., FastAPI],
    faker: Faker,
    free_tcp_port_factory: Callable[[], int],
) -> None:
    unavailable_redis_url = f"redis://127.0.0.1:{free_tcp_port_factory()}/0"
    app = app_factory(override_redis_url=unavailable_redis_url)
    request_id = faker.uuid4()

    with TestClient(app) as client:
        response = client.get(app.url_path_for("read_readiness"), headers={"X-Request-ID": request_id})

    payload = ReadinessProbe.model_validate(response.json())

    assert response.status_code == 503
    assert response.headers["x-request-id"] == request_id
    assert payload == ReadinessProbeFactory.build(
        status="error",
        service="Registries API",
        checks=(
            DependencyProbeFactory.build(name="postgres", status="ok", detail=None),
            DependencyProbeFactory.build(name="redis", status="error", detail="redis unavailable"),
        ),
    )


def test_health_returns_503_when_postgres_is_unreachable(
    app_factory: Callable[..., FastAPI],
    faker: Faker,
    free_tcp_port_factory: Callable[[], int],
) -> None:
    unavailable_postgres_dsn = (
        f"postgresql+asyncpg://registries:registries@127.0.0.1:{free_tcp_port_factory()}/registries"
    )
    app = app_factory(override_postgres_dsn=unavailable_postgres_dsn)
    correlation_id = faker.uuid4()

    with TestClient(app) as client:
        response = client.get(app.url_path_for("read_health"), headers={"X-Correlation-ID": correlation_id})

    payload = ReadinessProbe.model_validate(response.json())

    assert response.status_code == 503
    assert response.headers["x-correlation-id"] == correlation_id
    assert payload == ReadinessProbeFactory.build(
        status="error",
        service="Registries API",
        checks=(
            DependencyProbeFactory.build(name="postgres", status="error", detail="database unavailable"),
            DependencyProbeFactory.build(name="redis", status="ok", detail=None),
        ),
    )
