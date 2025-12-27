"""Tests for Core service API endpoints."""

from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


class TestCoreEndpoints:
    """Test Core service API endpoints."""

    def test_build_workflow_success(self):
        """Test successful workflow build."""
        response = client.post(
            "/v1/core/build",
            json={
                "project_id": "test-123",
                "workflow_spec": {"nodes": [], "edges": []},
                "options": {"timeout": 30},
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "build_id" in data
        assert "artifacts" in data

    def test_build_workflow_invalid_request(self):
        """Test build with invalid request."""
        response = client.post("/v1/core/build", json={})

        assert response.status_code == 422  # Validation error

    def test_validate_workflow_success(self):
        """Test successful workflow validation."""
        response = client.post(
            "/v1/core/validate",
            json={"workflow_spec": {"nodes": [], "edges": [], "config": {}}},
        )

        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert "errors" in data
        assert "warnings" in data

    def test_validate_workflow_empty_spec(self):
        """Test validation with empty spec."""
        response = client.post("/v1/core/validate", json={"workflow_spec": {}})

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["warnings"]) > 0

    def test_validate_workflow_invalid_request(self):
        """Test validation with invalid request."""
        response = client.post("/v1/core/validate", json={})

        assert response.status_code == 422  # Validation error

    def test_core_health_check(self):
        """Test Core service health check."""
        response = client.get("/v1/core/health")

        assert response.status_code == 200
        data = response.json()
        assert data["healthy"] is True
        assert data["mode"] == "mock"
        assert data["service"] == "flowbiz-ai-core"


class TestEndpointIntegration:
    """Integration tests for Core endpoints."""

    def test_build_then_validate(self):
        """Test building and then validating a workflow."""
        # First build
        build_response = client.post(
            "/v1/core/build",
            json={
                "project_id": "test-integration",
                "workflow_spec": {"nodes": [{"id": "1", "type": "start"}], "edges": []},
            },
        )

        assert build_response.status_code == 200

        # Then validate same spec
        validate_response = client.post(
            "/v1/core/validate",
            json={
                "workflow_spec": {"nodes": [{"id": "1", "type": "start"}], "edges": []}
            },
        )

        assert validate_response.status_code == 200
        validate_data = validate_response.json()
        assert validate_data["valid"] is True

    def test_full_workflow_api(self):
        """Test complete workflow through API."""
        # Check health
        health_response = client.get("/v1/core/health")
        assert health_response.status_code == 200
        assert health_response.json()["healthy"] is True

        # Validate spec
        validate_response = client.post(
            "/v1/core/validate",
            json={"workflow_spec": {"nodes": [], "edges": [], "config": {}}},
        )
        assert validate_response.status_code == 200
        assert validate_response.json()["valid"] is True

        # Build workflow
        build_response = client.post(
            "/v1/core/build",
            json={
                "project_id": "test-full-workflow",
                "workflow_spec": {"nodes": [], "edges": [], "config": {}},
            },
        )
        assert build_response.status_code == 200
        assert build_response.json()["status"] == "success"
