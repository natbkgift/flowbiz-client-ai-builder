"""
Core service API endpoints.

Provides endpoints for interacting with the FlowBiz AI Core system
for building and validating workflows.
"""

from fastapi import APIRouter, HTTPException, status

from packages.core.config import settings
from packages.core.contracts import BuildRequest, ValidationRequest
from packages.core.gateway import CoreServiceMode, get_core_service

router = APIRouter(prefix="/v1/core", tags=["core"])


@router.post("/build")
async def build_workflow(request: BuildRequest):
    """
    Build a workflow in the Core system.

    Args:
        request: Build request with workflow specification

    Returns:
        Build response with build ID and status

    Raises:
        HTTPException: If build fails
    """
    try:
        mode = CoreServiceMode(settings.core_service_mode)
        service = get_core_service(mode)
        response = await service.build_workflow(request)

        if response.status == "failed":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.message,
            )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid configuration: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Build failed: {str(e)}",
        )


@router.post("/validate")
async def validate_workflow(request: ValidationRequest):
    """
    Validate a workflow specification.

    Args:
        request: Validation request with workflow spec

    Returns:
        Validation response with errors and warnings

    Raises:
        HTTPException: If validation service fails
    """
    try:
        mode = CoreServiceMode(settings.core_service_mode)
        service = get_core_service(mode)
        response = await service.validate_workflow(request)

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid configuration: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}",
        )


@router.get("/health")
async def core_health():
    """
    Check Core service health.

    Returns:
        Health status of Core service connection

    Raises:
        HTTPException: If Core service is unreachable
    """
    try:
        mode = CoreServiceMode(settings.core_service_mode)
        service = get_core_service(mode)
        healthy = await service.health_check()

        return {
            "healthy": healthy,
            "mode": settings.core_service_mode,
            "service": "flowbiz-ai-core",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Core service health check failed: {str(e)}",
        )
