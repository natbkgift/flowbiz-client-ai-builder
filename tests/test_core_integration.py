"""Tests for Core service contracts and integration."""

import pytest

from packages.core.adapters import MockCoreService
from packages.core.contracts import BuildRequest, ValidationRequest
from packages.core.gateway import CoreServiceGateway, CoreServiceMode, get_core_service


class TestContracts:
    """Test contract models."""

    def test_build_request_creation(self):
        """Test BuildRequest model creation."""
        request = BuildRequest(
            project_id="test-123",
            workflow_spec={"nodes": [], "edges": []},
            options={"timeout": 30},
        )
        assert request.project_id == "test-123"
        assert request.workflow_spec == {"nodes": [], "edges": []}
        assert request.options == {"timeout": 30}

    def test_validation_request_creation(self):
        """Test ValidationRequest model creation."""
        request = ValidationRequest(workflow_spec={"nodes": [], "edges": []})
        assert request.workflow_spec == {"nodes": [], "edges": []}


class TestMockCoreService:
    """Test mock Core service adapter."""

    @pytest.mark.asyncio
    async def test_build_workflow_success(self):
        """Test successful workflow build."""
        service = MockCoreService()
        request = BuildRequest(
            project_id="test-123", workflow_spec={"nodes": [], "edges": []}
        )

        response = await service.build_workflow(request)

        assert response.status == "success"
        assert response.build_id
        assert response.artifacts is not None
        assert "workflow_id" in response.artifacts

    @pytest.mark.asyncio
    async def test_build_workflow_with_failures(self):
        """Test workflow build with simulated failures."""
        service = MockCoreService(simulate_failures=True)
        request = BuildRequest(
            project_id="test-123", workflow_spec={"nodes": [], "edges": []}
        )

        # Call 5 times to trigger a failure
        for i in range(5):
            response = await service.build_workflow(request)
            if i == 4:
                assert response.status == "failed"
                assert response.artifacts is None
            else:
                assert response.status == "success"

    @pytest.mark.asyncio
    async def test_validate_workflow_success(self):
        """Test workflow validation with valid spec."""
        service = MockCoreService()
        request = ValidationRequest(
            workflow_spec={"nodes": [], "edges": [], "config": {}}
        )

        response = await service.validate_workflow(request)

        assert response.valid is True
        assert len(response.errors) == 0
        # Warnings are OK for empty nodes/edges in mock

    @pytest.mark.asyncio
    async def test_validate_workflow_empty_spec(self):
        """Test workflow validation with empty spec."""
        service = MockCoreService()
        request = ValidationRequest(workflow_spec={})

        response = await service.validate_workflow(request)

        assert response.valid is False
        assert len(response.warnings) > 0

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check."""
        service = MockCoreService()
        healthy = await service.health_check()
        assert healthy is True

    def test_call_counter(self):
        """Test call counter functionality."""
        service = MockCoreService()
        assert service.get_call_count() == 0

        service.reset()
        assert service.get_call_count() == 0


class TestCoreServiceGateway:
    """Test Core service gateway."""

    def test_create_mock_service(self):
        """Test creating mock service via gateway."""
        service = CoreServiceGateway.create(CoreServiceMode.MOCK)
        assert isinstance(service, MockCoreService)

    def test_create_real_service_not_implemented(self):
        """Test that real service raises NotImplementedError."""
        with pytest.raises(NotImplementedError, match="not yet implemented"):
            CoreServiceGateway.create(CoreServiceMode.REAL)

    def test_get_core_service_convenience(self):
        """Test convenience function."""
        service = get_core_service(CoreServiceMode.MOCK)
        assert isinstance(service, MockCoreService)

    def test_get_core_service_default_mock(self):
        """Test that default mode is mock."""
        service = get_core_service()
        assert isinstance(service, MockCoreService)
