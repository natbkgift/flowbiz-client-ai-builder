"""FlowBiz AI Builder v11 control-plane contracts.

PR-18 intentionally defines deterministic, side-effect-free contracts only.
No host, Docker, SSH, database, Nginx, or production mutation is performed here.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class InfrastructureMode(str, Enum):
    SINGLE_VPS = "single-vps"
    DISTRIBUTED = "distributed"


class ProjectMode(str, Enum):
    STANDARD = "standard"
    CUSTOM = "custom"
    ADVANCED = "advanced"
    LEGACY = "legacy"


class ProjectRepository(BaseModel):
    provider: Literal["github"] = "github"
    full_name: str = Field(..., pattern=r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
    default_branch: str = "main"


class RuntimeTarget(BaseModel):
    host_alias: str = "flowbiz-vps"
    root: str = Field(..., pattern=r"^/opt/flowbiz/clients/[A-Za-z0-9_.-]+/?$")


class RunnerConfig(BaseModel):
    authority: Literal["flowbiz-runner"] = "flowbiz-runner"
    ephemeral_jobs: bool = True
    max_concurrency: int = Field(default=1, ge=1)
    production_guard: bool = True


class ReleaseConfig(BaseModel):
    exact_sha: bool = True
    immutable: bool = True
    rollback: bool = True


class CustomizationPolicy(BaseModel):
    source_code: bool = True
    database: bool = True
    services: bool = True
    infrastructure: Literal["controlled", "locked"] = "controlled"


class ProjectManifest(BaseModel):
    project_id: str = Field(..., pattern=r"^[a-z0-9][a-z0-9._-]*$")
    mode: ProjectMode = ProjectMode.STANDARD
    infrastructure_mode: InfrastructureMode = InfrastructureMode.SINGLE_VPS
    repository: ProjectRepository
    runtime: RuntimeTarget
    services: list[str] = Field(default_factory=list)
    runner: RunnerConfig = Field(default_factory=RunnerConfig)
    release: ReleaseConfig = Field(default_factory=ReleaseConfig)
    customization: CustomizationPolicy = Field(default_factory=CustomizationPolicy)

    @model_validator(mode="after")
    def validate_v11_baseline(self) -> "ProjectManifest":
        if self.infrastructure_mode == InfrastructureMode.SINGLE_VPS:
            if self.runner.max_concurrency != 1:
                raise ValueError("single-vps mode requires runner.max_concurrency=1")
            if not self.runner.ephemeral_jobs or not self.runner.production_guard:
                raise ValueError(
                    "single-vps mode requires ephemeral jobs and production resource guard"
                )

        if not (self.release.exact_sha and self.release.immutable and self.release.rollback):
            raise ValueError(
                "v11 release baseline requires exact_sha, immutable releases, and rollback"
            )

        if len(set(self.services)) != len(self.services):
            raise ValueError("project services must be unique")

        return self


class ProjectRecord(BaseModel):
    manifest: ProjectManifest
    generation: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProvisioningOperation(str, Enum):
    ENSURE_PROJECT_ROOT = "ensure-project-root"
    ENSURE_RELEASE_LAYOUT = "ensure-release-layout"
    ENSURE_SHARED_LAYOUT = "ensure-shared-layout"
    DECLARE_SERVICE = "declare-service"
    DECLARE_HEALTH_CHECK = "declare-health-check"
    DECLARE_BACKUP_POLICY = "declare-backup-policy"


class ProvisioningStep(BaseModel):
    step_id: str
    operation: ProvisioningOperation
    target: str
    risk_class: Literal["low", "medium", "high"] = "low"
    approval_required: bool = False


class ProvisioningPlan(BaseModel):
    plan_id: str
    project_id: str
    infrastructure_mode: InfrastructureMode
    steps: list[ProvisioningStep]
    plan_only: Literal[True] = True
    execution_permitted: Literal[False] = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ControlPlaneRunState(str, Enum):
    PLANNED = "planned"
    READY_FOR_CI = "ready-for-ci"
    CI_RUNNING = "ci-running"
    CI_PASSED = "ci-passed"
    READY_FOR_RELEASE = "ready-for-release"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class ControlPlaneRun(BaseModel):
    run_id: str
    project_id: str
    exact_sha: str | None = Field(default=None, pattern=r"^[0-9a-f]{40}$")
    state: ControlPlaneRunState = ControlPlaneRunState.PLANNED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reason: str | None = None


__all__ = [
    "ControlPlaneRun",
    "ControlPlaneRunState",
    "CustomizationPolicy",
    "InfrastructureMode",
    "ProjectManifest",
    "ProjectMode",
    "ProjectRecord",
    "ProjectRepository",
    "ProvisioningOperation",
    "ProvisioningPlan",
    "ProvisioningStep",
    "ReleaseConfig",
    "RunnerConfig",
    "RuntimeTarget",
]
