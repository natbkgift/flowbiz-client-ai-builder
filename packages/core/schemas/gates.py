"""Gate definitions for PR validation pipeline."""

from enum import Enum

from pydantic import BaseModel, Field


class GateType(str, Enum):
    """Types of gates in the validation pipeline."""

    SAFETY = "safety"  # Gate -1
    PLANNING = "planning"  # Gate 0
    CI = "ci"  # Gate 1
    STAGING = "staging"  # Gate 2
    PRODUCTION = "production"  # Gate 3
    LEARNING = "learning"  # Gate 4


class GateStatus(str, Enum):
    """Status of a gate validation."""

    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class SafetyGateResult(BaseModel):
    """Results from Safety Gate (Gate -1)."""

    forbidden_paths_checked: bool = Field(..., description="No forbidden paths were touched")
    secrets_checked: bool = Field(..., description="No secrets leaked")
    permissions_valid: bool = Field(..., description="Permissions are valid")
    status: GateStatus = GateStatus.PENDING


class PlanningGateResult(BaseModel):
    """Results from Planning Gate (Gate 0)."""

    prd_provided: bool = Field(..., description="PRD or DoD provided by BA")
    test_plan_provided: bool = Field(..., description="Test plan provided by QA")
    deploy_plan_provided: bool = Field(..., description="Deploy and verify plan provided by SRE")
    status: GateStatus = GateStatus.PENDING


class CIGateResult(BaseModel):
    """Results from CI Gate (Gate 1)."""

    lint_passed: bool = Field(..., description="Linting passed")
    unit_tests_passed: bool = Field(..., description="Unit tests passed")
    security_scan_passed: bool = Field(..., description="Security scan passed")
    dependency_check_passed: bool = Field(
        ..., description="Dependency and budget policy check passed"
    )
    status: GateStatus = GateStatus.PENDING


class StagingGateResult(BaseModel):
    """Results from Staging Gate (Gate 2)."""

    deployed_to_staging: bool = Field(..., description="PR SHA deployed to staging")
    smoke_tests_passed: bool = Field(..., description="Smoke tests passed on staging")
    evidence_attached: bool = Field(..., description="Evidence of successful deployment attached")
    status: GateStatus = GateStatus.PENDING


class ProductionGateResult(BaseModel):
    """Results from Production Gate (Gate 3)."""

    deployed_to_production: bool = Field(..., description="Main SHA deployed to production")
    verification_passed: bool = Field(..., description="Production verification passed")
    rollback_ready: bool = Field(..., description="Auto rollback configured and ready")
    status: GateStatus = GateStatus.PENDING


class LearningGateResult(BaseModel):
    """Results from Learning Gate (Gate 4)."""

    post_run_report_generated: bool = Field(..., description="Post-run report generated")
    knowledge_artifacts_created: bool = Field(..., description="Knowledge artifacts created")
    suggestion_created: bool = Field(
        False, description="Suggestion PR or issue created if improvements identified"
    )
    status: GateStatus = GateStatus.PENDING


class GatePipeline(BaseModel):
    """Complete gate pipeline for a PR."""

    pr_number: int
    safety_gate: SafetyGateResult
    planning_gate: PlanningGateResult
    ci_gate: CIGateResult
    staging_gate: StagingGateResult
    production_gate: ProductionGateResult
    learning_gate: LearningGateResult

    def is_ready_for_merge(self) -> bool:
        """Check if all gates up to CI are passed."""
        return (
            self.safety_gate.status == GateStatus.PASSED
            and self.planning_gate.status == GateStatus.PASSED
            and self.ci_gate.status == GateStatus.PASSED
        )

    def is_production_ready(self) -> bool:
        """Check if all gates up to production are passed."""
        return (
            self.is_ready_for_merge()
            and self.staging_gate.status == GateStatus.PASSED
            and self.production_gate.status == GateStatus.PASSED
        )
