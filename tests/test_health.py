from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_health_check_returns_200():
    """Test that health check returns 200 status code."""
    response = client.get("/healthz")
    assert response.status_code == 200


def test_health_check_response_structure():
    """Test that health check returns correct JSON structure."""
    response = client.get("/healthz")
    data = response.json()

    assert "status" in data
    assert "service" in data
    assert "version" in data


def test_health_check_status_ok():
    """Test that health check returns ok status."""
    response = client.get("/healthz")
    data = response.json()

    assert data["status"] == "ok"


def test_health_check_service_name():
    """Test that health check returns service name."""
    from packages.core.config import settings

    response = client.get("/healthz")
    data = response.json()

    assert data["service"] == settings.flowbiz_service_name


def test_health_check_version():
    """Test that health check returns version."""
    from packages.core.config import settings

    response = client.get("/healthz")
    data = response.json()

    assert data["version"] == settings.flowbiz_version


def test_readyz_returns_200():
    """Test that readiness check returns 200 status code."""
    response = client.get("/readyz")
    assert response.status_code == 200


def test_readyz_response_structure():
    """Test that readiness check returns correct JSON structure."""
    response = client.get("/readyz")
    data = response.json()

    assert "status" in data
    assert "service" in data
    assert "version" in data


def test_readyz_status_ready():
    """Test that readiness check returns ready status."""
    response = client.get("/readyz")
    data = response.json()

    assert data["status"] == "ready"


def test_version_returns_200():
    """Test that version endpoint returns 200 status code."""
    response = client.get("/version")
    assert response.status_code == 200


def test_version_response_structure():
    """Test that version endpoint returns correct JSON structure."""
    response = client.get("/version")
    data = response.json()

    assert "status" in data
    assert "service" in data
    assert "version" in data


def test_version_info():
    """Test that version endpoint returns correct version info."""
    from packages.core.config import settings

    response = client.get("/version")
    data = response.json()

    assert data["version"] == settings.flowbiz_version
    assert data["service"] == settings.flowbiz_service_name
