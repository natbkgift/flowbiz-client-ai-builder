"""
Mock implementation of Core service for development and testing.

This adapter provides a stub implementation that can be used without
a real Core system connection.
"""

import uuid

from packages.core.contracts import (
    BuildRequest,
    BuildResponse,
    ICoreService,
    ValidationRequest,
    ValidationResponse,
)


class MockCoreService(ICoreService):
    """
    Mock implementation of Core service interface.

    This adapter is used for:
    - Local development without Core system
    - Testing client logic independently
    - CI/CD pipeline validation
    """

    def __init__(self, simulate_failures: bool = False):
        """
        Initialize mock service.

        Args:
            simulate_failures: If True, occasionally return failures for testing
        """
        self.simulate_failures = simulate_failures
        self._call_count = 0

    async def build_workflow(self, request: BuildRequest) -> BuildResponse:
        """Mock build workflow operation."""
        self._call_count += 1

        # Simulate occasional failure if configured
        if self.simulate_failures and self._call_count % 5 == 0:
            return BuildResponse(
                build_id=str(uuid.uuid4()),
                status="failed",
                message="Mock failure for testing",
                artifacts=None,
            )

        # Normal success response
        return BuildResponse(
            build_id=str(uuid.uuid4()),
            status="success",
            message=f"Mock build completed for project {request.project_id}",
            artifacts={
                "workflow_id": str(uuid.uuid4()),
                "deployment_url": "https://mock.example.com/workflow",
            },
        )

    async def validate_workflow(
        self, request: ValidationRequest
    ) -> ValidationResponse:
        """Mock workflow validation."""
        self._call_count += 1

        # Basic validation checks on mock data
        errors = []
        warnings = []

        if not request.workflow_spec:
            errors.append("Workflow spec cannot be empty")

        if "nodes" not in request.workflow_spec:
            warnings.append("No nodes defined in workflow")

        if "edges" not in request.workflow_spec:
            warnings.append("No edges defined in workflow")

        return ValidationResponse(
            valid=len(errors) == 0, errors=errors, warnings=warnings
        )

    async def health_check(self) -> bool:
        """Mock health check - always returns True."""
        return True

    def get_call_count(self) -> int:
        """Get number of calls made (for testing)."""
        return self._call_count

    def reset(self) -> None:
        """Reset call counter (for testing)."""
        self._call_count = 0
