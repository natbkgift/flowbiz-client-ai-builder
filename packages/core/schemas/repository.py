"""Multi-repository operations and repository management."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RepositoryStatus(str, Enum):
    """Status of a repository in the platform."""

    PENDING = "pending"
    READY = "ready"
    ONBOARDING = "onboarding"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class RepositoryType(str, Enum):
    """Type of repository based on stack."""

    FASTAPI = "fastapi"
    NODEJS = "nodejs"
    WORKER = "worker"
    CRON = "cron"
    FRONTEND = "frontend"
    UNKNOWN = "unknown"


class Repository(BaseModel):
    """Repository definition in the multi-repo platform."""

    repo_id: str
    owner: str
    name: str
    full_name: str = Field(..., description="Full repository name (owner/name)")
    repo_type: RepositoryType
    status: RepositoryStatus = RepositoryStatus.PENDING
    default_branch: str = "main"
    linked_at: datetime = Field(default_factory=datetime.utcnow)


class ReadinessCheckResult(BaseModel):
    """Results from repository readiness check."""

    repo_id: str
    has_pr_template: bool = Field(..., description="Has PR template")
    has_ci_workflow: bool = Field(..., description="Has CI workflow")
    has_required_files: bool = Field(..., description="Has required files (README, etc.)")
    follows_standards: bool = Field(..., description="Follows coding standards")
    has_health_endpoints: bool = Field(False, description="Has health endpoints (if applicable)")
    issues_found: list[str] = Field(default_factory=list, description="Issues found during check")
    ready: bool = Field(..., description="Overall readiness status")
    checked_at: datetime = Field(default_factory=datetime.utcnow)


class OnboardingPR(BaseModel):
    """Onboarding PR to bring a repository up to standards."""

    onboarding_id: str
    repo_id: str
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    changes_needed: list[str] = Field(..., description="List of changes to be made")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed: bool = False


class EnvironmentType(str, Enum):
    """Environment types."""

    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "production"


class Environment(BaseModel):
    """Environment configuration."""

    environment_id: str
    repo_id: str
    environment_type: EnvironmentType
    url: Optional[str] = None
    requires_approval: bool = False
    approvers: list[str] = Field(default_factory=list)


class DeploymentLock(BaseModel):
    """Lock for preventing concurrent deployments."""

    lock_id: str
    repo_id: str
    environment: EnvironmentType
    locked_by: str = Field(..., description="Workflow or user that acquired the lock")
    locked_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class Deployment(BaseModel):
    """Deployment record."""

    deployment_id: str
    repo_id: str
    environment: EnvironmentType
    commit_sha: str
    pr_number: Optional[int] = None
    deployed_by: str
    deployed_at: datetime = Field(default_factory=datetime.utcnow)
    verified: bool = False
    rolled_back: bool = False


class ProjectLock(BaseModel):
    """Lock for project-level operations."""

    lock_id: str
    repo_id: str
    operation: str = Field(..., description="Operation being performed")
    locked_by: str
    locked_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class VersionInfo(BaseModel):
    """Version tracking per environment."""

    repo_id: str
    environment: EnvironmentType
    version: str = Field(..., description="Semantic version")
    commit_sha: str
    deployed_at: datetime = Field(default_factory=datetime.utcnow)
