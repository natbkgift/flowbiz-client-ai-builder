"""Workflow definitions for PR automation and orchestration."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class WorkflowPhase(str, Enum):
    """Phases of the Human-Inspired Engineering Model."""

    DISCOVERY = "discovery"
    PLAN = "plan"
    BUILD = "build"
    RELEASE = "release"
    LEARN = "learn"


class WorkflowStatus(str, Enum):
    """Status of a workflow execution."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class PRWorkflow(BaseModel):
    """PR workflow tracking."""

    workflow_id: str
    pr_number: Optional[int] = None
    branch_name: str
    phase: WorkflowPhase
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class DiscoveryPhaseOutput(BaseModel):
    """Output from Discovery phase."""

    requirements_gathered: bool = Field(..., description="Requirements were gathered")
    problem_statement: str = Field(..., description="Clear problem statement")
    stakeholders_identified: list[str] = Field(
        default_factory=list, description="Stakeholders identified"
    )
    constraints: list[str] = Field(default_factory=list, description="Known constraints")


class PlanPhaseOutput(BaseModel):
    """Output from Plan phase."""

    squad_assembled: bool = Field(..., description="Feature squad assembled")
    acceptance_criteria_defined: bool = Field(..., description="Acceptance criteria defined")
    test_plan_created: bool = Field(..., description="Test plan created")
    deployment_plan_created: bool = Field(..., description="Deployment plan created")
    scope_locked: bool = Field(..., description="Scope is locked and agreed upon")


class BuildPhaseOutput(BaseModel):
    """Output from Build phase."""

    code_written: bool = Field(..., description="Code implementation completed")
    tests_written: bool = Field(..., description="Tests written and passing")
    code_reviewed: bool = Field(..., description="Code reviewed by peers")
    security_reviewed: bool = Field(..., description="Security reviewed")
    documentation_updated: bool = Field(..., description="Documentation updated")


class ReleasePhaseOutput(BaseModel):
    """Output from Release phase."""

    deployed_to_staging: bool = Field(..., description="Deployed to staging")
    staging_verified: bool = Field(..., description="Staging environment verified")
    deployed_to_production: bool = Field(..., description="Deployed to production")
    production_verified: bool = Field(..., description="Production environment verified")
    rollback_tested: bool = Field(..., description="Rollback procedure tested")


class LearnPhaseOutput(BaseModel):
    """Output from Learn phase."""

    knowledge_artifacts_created: bool = Field(..., description="Knowledge artifacts created")
    metrics_collected: bool = Field(..., description="Metrics collected")
    improvements_identified: bool = Field(..., description="Improvements identified")
    automation_opportunities_documented: bool = Field(
        ..., description="Automation opportunities documented"
    )


class WorkflowExecution(BaseModel):
    """Complete workflow execution record."""

    workflow_id: str
    pr_number: int
    squad_id: str
    feature_name: str
    discovery: Optional[DiscoveryPhaseOutput] = None
    plan: Optional[PlanPhaseOutput] = None
    build: Optional[BuildPhaseOutput] = None
    release: Optional[ReleasePhaseOutput] = None
    learn: Optional[LearnPhaseOutput] = None
    current_phase: WorkflowPhase
    status: WorkflowStatus
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class ApprovalRequired(BaseModel):
    """Represents a point where human approval is required."""

    approval_id: str
    workflow_id: str
    reason: str = Field(..., description="Reason approval is required")
    approval_type: str = Field(
        ..., description="Type of approval: workflow_approval, environment_approval, breaking_api"
    )
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    approved: Optional[bool] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    comments: Optional[str] = None
    auto_approve_enabled: bool = Field(
        default=False, description="Whether auto-approval is enabled for this approval"
    )

    def auto_approve(self, approver: str = "system") -> None:
        """Automatically approve this workflow approval.

        Args:
            approver: The name of the auto-approver (default: "system")
        """
        if self.auto_approve_enabled:
            self.approved = True
            self.approved_by = approver
            self.approved_at = datetime.utcnow()
            self.comments = "Auto-approved by system"


class AutoApprovalConfig(BaseModel):
    """Configuration for auto-approval rules."""

    enabled: bool = Field(default=False, description="Global auto-approval toggle")
    approval_types: list[str] = Field(
        default_factory=list,
        description=(
            "List of approval types that can be auto-approved "
            "(e.g., 'workflow_approval', 'environment_approval')"
        ),
    )
    excluded_workflows: list[str] = Field(
        default_factory=list,
        description="List of workflow IDs that should never be auto-approved",
    )
    require_ci_pass: bool = Field(
        default=True,
        description="Require CI to pass before auto-approval",
    )

    def can_auto_approve(
        self, approval: ApprovalRequired, ci_passed: bool = False
    ) -> bool:
        """Check if an approval can be auto-approved based on the configuration.

        Args:
            approval: The approval to check
            ci_passed: Whether CI has passed

        Returns:
            True if the approval can be auto-approved, False otherwise
        """
        if not self.enabled:
            return False

        if approval.workflow_id in self.excluded_workflows:
            return False

        if self.require_ci_pass and not ci_passed:
            return False

        if approval.approval_type not in self.approval_types:
            return False

        return True


class HotfixWorkflow(BaseModel):
    """Special workflow for hotfix PRs."""

    hotfix_id: str
    original_pr_number: int
    hotfix_pr_number: Optional[int] = None
    issue_description: str = Field(..., description="Description of the issue requiring hotfix")
    triggered_by: str = Field(..., description="What triggered the hotfix (e.g., failed check)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
