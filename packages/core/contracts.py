"""
Contract definitions for Core system integration.

These contracts define the interface between the AI Builder client
and the FlowBiz AI Core system, following contract-first design principles.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

# Request/Response Models (Contracts)


class BuildRequest(BaseModel):
    """Request to build an AI workflow or component."""

    project_id: str
    workflow_spec: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None


class BuildResponse(BaseModel):
    """Response from a build operation."""

    build_id: str
    status: str
    message: str
    artifacts: Optional[Dict[str, Any]] = None


class ValidationRequest(BaseModel):
    """Request to validate a workflow specification."""

    workflow_spec: Dict[str, Any]


class ValidationResponse(BaseModel):
    """Response from validation operation."""

    valid: bool
    errors: List[str] = []
    warnings: List[str] = []


# Core Service Interface (Contract)


class ICoreService(ABC):
    """
    Interface for FlowBiz AI Core service integration.

    This contract must be implemented by all Core service adapters,
    ensuring consistent behavior across mock and real implementations.
    """

    @abstractmethod
    async def build_workflow(self, request: BuildRequest) -> BuildResponse:
        """
        Build a workflow in the Core system.

        Args:
            request: Build request with workflow specification

        Returns:
            BuildResponse with build status and artifacts
        """
        pass

    @abstractmethod
    async def validate_workflow(
        self, request: ValidationRequest
    ) -> ValidationResponse:
        """
        Validate a workflow specification.

        Args:
            request: Validation request with workflow spec

        Returns:
            ValidationResponse with validation results
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if Core service is healthy and reachable.

        Returns:
            True if service is healthy, False otherwise
        """
        pass
