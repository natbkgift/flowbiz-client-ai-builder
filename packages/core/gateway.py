"""
Gateway for Core service integration.

Provides a factory pattern for creating the appropriate Core service
adapter based on configuration (mock vs real).
"""

from enum import Enum

from packages.core.adapters import MockCoreService
from packages.core.contracts import ICoreService


class CoreServiceMode(str, Enum):
    """Core service integration mode."""

    MOCK = "mock"
    REAL = "real"


class CoreServiceGateway:
    """
    Gateway for Core service integration.

    This factory creates the appropriate adapter based on configuration,
    enabling easy switching between mock and real implementations.
    """

    @staticmethod
    def create(mode: CoreServiceMode = CoreServiceMode.MOCK) -> ICoreService:
        """
        Create Core service adapter based on mode.

        Args:
            mode: Service mode (mock or real)

        Returns:
            Core service adapter implementing ICoreService

        Raises:
            NotImplementedError: If real mode is requested (not yet implemented)
        """
        if mode == CoreServiceMode.MOCK:
            return MockCoreService()
        elif mode == CoreServiceMode.REAL:
            # Real implementation will be added in future phase
            raise NotImplementedError(
                "Real Core service integration not yet implemented. "
                "Use CoreServiceMode.MOCK for now."
            )
        else:
            raise ValueError(f"Unknown core service mode: {mode}")


# Convenience function
def get_core_service(mode: CoreServiceMode = CoreServiceMode.MOCK) -> ICoreService:
    """
    Get Core service instance.

    This is a convenience function that wraps CoreServiceGateway.create().

    Args:
        mode: Service mode (mock or real)

    Returns:
        Core service adapter
    """
    return CoreServiceGateway.create(mode)
