"""Gate Framework v1 - Unified gate validation system with state machine.

This module implements the Gate Framework as specified in BLUEPRINT.md PR #14,
providing a unified system for running all gates (Safety, Planning, CI, Staging,
Production, Learning) with a state machine to track run execution.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from packages.core.schemas.gates import (
    CIGateResult,
    GatePipeline,
    GateStatus,
    GateType,
    LearningGateResult,
    PlanningGateResult,
    ProductionGateResult,
    SafetyGateResult,
    StagingGateResult,
)


class RunState(str, Enum):
    """State machine states for a gate run."""

    INITIALIZED = "initialized"
    RUNNING_SAFETY = "running_safety"
    RUNNING_PLANNING = "running_planning"
    RUNNING_CI = "running_ci"
    RUNNING_STAGING = "running_staging"
    RUNNING_PRODUCTION = "running_production"
    RUNNING_LEARNING = "running_learning"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class RunResult(str, Enum):
    """Overall result of a gate run."""

    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


class GateRunConfig(BaseModel):
    """Configuration for a gate run."""

    pr_number: int
    run_id: str
    skip_staging: bool = Field(
        default=False,
        description="Skip staging gate (for local dev environments)",
    )
    skip_production: bool = Field(
        default=False,
        description="Skip production gate (for non-production deployments)",
    )
    mock_mode: bool = Field(
        default=True,
        description="Run in mock mode (no actual deployments)",
    )


class GateRun(BaseModel):
    """A single gate run through the gate framework."""

    run_id: str
    pr_number: int
    config: GateRunConfig
    state: RunState = RunState.INITIALIZED
    result: RunResult = RunResult.PENDING
    current_gate: Optional[GateType] = None
    pipeline: Optional[GatePipeline] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    blocked_reason: Optional[str] = None

    def get_progress_percentage(self) -> int:
        """Get the progress percentage through gates.

        Returns:
            Integer percentage from 0 to 100.
        """
        state_progress = {
            RunState.INITIALIZED: 0,
            RunState.RUNNING_SAFETY: 10,
            RunState.RUNNING_PLANNING: 25,
            RunState.RUNNING_CI: 40,
            RunState.RUNNING_STAGING: 60,
            RunState.RUNNING_PRODUCTION: 80,
            RunState.RUNNING_LEARNING: 95,
            RunState.COMPLETED: 100,
            RunState.BLOCKED: -1,
            RunState.FAILED: -1,
        }
        return state_progress.get(self.state, 0)


class GateFramework:
    """Unified gate validation framework with state machine.

    This framework orchestrates running through all gates in sequence,
    tracking state transitions and collecting results.
    """

    def __init__(self, config: GateRunConfig) -> None:
        """Initialize the gate framework.

        Args:
            config: Configuration for the gate run.
        """
        self.config = config
        self.run = GateRun(
            run_id=config.run_id,
            pr_number=config.pr_number,
            config=config,
        )

    def start_run(self) -> GateRun:
        """Start a new gate run.

        Returns:
            The initialized GateRun object.
        """
        self.run.state = RunState.RUNNING_SAFETY
        self.run.current_gate = GateType.SAFETY
        return self.run

    def execute_safety_gate(
        self,
        forbidden_paths_checked: bool = True,
        secrets_checked: bool = True,
        permissions_valid: bool = True,
    ) -> SafetyGateResult:
        """Execute the safety gate.

        Args:
            forbidden_paths_checked: No forbidden paths were touched.
            secrets_checked: No secrets leaked.
            permissions_valid: Permissions are valid.

        Returns:
            SafetyGateResult with the gate outcome.
        """
        all_passed = forbidden_paths_checked and secrets_checked and permissions_valid
        status = GateStatus.PASSED if all_passed else GateStatus.FAILED

        result = SafetyGateResult(
            forbidden_paths_checked=forbidden_paths_checked,
            secrets_checked=secrets_checked,
            permissions_valid=permissions_valid,
            status=status,
        )

        if status == GateStatus.PASSED:
            self.run.state = RunState.RUNNING_PLANNING
            self.run.current_gate = GateType.PLANNING
        else:
            self._fail_run("Safety gate failed")

        return result

    def execute_planning_gate(
        self,
        prd_provided: bool = True,
        test_plan_provided: bool = True,
        deploy_plan_provided: bool = True,
    ) -> PlanningGateResult:
        """Execute the planning gate.

        Args:
            prd_provided: PRD or DoD provided by BA.
            test_plan_provided: Test plan provided by QA.
            deploy_plan_provided: Deploy and verify plan provided by SRE.

        Returns:
            PlanningGateResult with the gate outcome.
        """
        all_passed = prd_provided and test_plan_provided and deploy_plan_provided
        status = GateStatus.PASSED if all_passed else GateStatus.FAILED

        result = PlanningGateResult(
            prd_provided=prd_provided,
            test_plan_provided=test_plan_provided,
            deploy_plan_provided=deploy_plan_provided,
            status=status,
        )

        if status == GateStatus.PASSED:
            self.run.state = RunState.RUNNING_CI
            self.run.current_gate = GateType.CI
        else:
            self._fail_run("Planning gate failed")

        return result

    def execute_ci_gate(
        self,
        lint_passed: bool = True,
        unit_tests_passed: bool = True,
        security_scan_passed: bool = True,
        dependency_check_passed: bool = True,
    ) -> CIGateResult:
        """Execute the CI gate.

        Args:
            lint_passed: Linting passed.
            unit_tests_passed: Unit tests passed.
            security_scan_passed: Security scan passed.
            dependency_check_passed: Dependency and budget policy check passed.

        Returns:
            CIGateResult with the gate outcome.
        """
        all_passed = (
            lint_passed and unit_tests_passed and security_scan_passed and dependency_check_passed
        )
        status = GateStatus.PASSED if all_passed else GateStatus.FAILED

        result = CIGateResult(
            lint_passed=lint_passed,
            unit_tests_passed=unit_tests_passed,
            security_scan_passed=security_scan_passed,
            dependency_check_passed=dependency_check_passed,
            status=status,
        )

        if status == GateStatus.PASSED:
            if self.config.skip_staging:
                self.run.state = RunState.RUNNING_PRODUCTION
                self.run.current_gate = GateType.PRODUCTION
            else:
                self.run.state = RunState.RUNNING_STAGING
                self.run.current_gate = GateType.STAGING
        else:
            self._fail_run("CI gate failed")

        return result

    def execute_staging_gate(
        self,
        deployed_to_staging: bool = True,
        smoke_tests_passed: bool = True,
        evidence_attached: bool = True,
    ) -> StagingGateResult:
        """Execute the staging gate.

        Args:
            deployed_to_staging: PR SHA deployed to staging.
            smoke_tests_passed: Smoke tests passed on staging.
            evidence_attached: Evidence of successful deployment attached.

        Returns:
            StagingGateResult with the gate outcome.
        """
        if self.config.skip_staging:
            # State was already advanced by CI gate when skip_staging=True
            # But ensure state is correct if called out of order
            if self.run.state == RunState.RUNNING_STAGING:
                if self.config.skip_production:
                    self.run.state = RunState.RUNNING_LEARNING
                    self.run.current_gate = GateType.LEARNING
                else:
                    self.run.state = RunState.RUNNING_PRODUCTION
                    self.run.current_gate = GateType.PRODUCTION
            return StagingGateResult(
                deployed_to_staging=False,
                smoke_tests_passed=False,
                evidence_attached=False,
                status=GateStatus.SKIPPED,
            )

        all_passed = deployed_to_staging and smoke_tests_passed and evidence_attached
        status = GateStatus.PASSED if all_passed else GateStatus.FAILED

        result = StagingGateResult(
            deployed_to_staging=deployed_to_staging,
            smoke_tests_passed=smoke_tests_passed,
            evidence_attached=evidence_attached,
            status=status,
        )

        if status == GateStatus.PASSED:
            if self.config.skip_production:
                self.run.state = RunState.RUNNING_LEARNING
                self.run.current_gate = GateType.LEARNING
            else:
                self.run.state = RunState.RUNNING_PRODUCTION
                self.run.current_gate = GateType.PRODUCTION
        else:
            self._fail_run("Staging gate failed")

        return result

    def execute_production_gate(
        self,
        deployed_to_production: bool = True,
        verification_passed: bool = True,
        rollback_ready: bool = True,
    ) -> ProductionGateResult:
        """Execute the production gate.

        Args:
            deployed_to_production: Main SHA deployed to production.
            verification_passed: Production verification passed.
            rollback_ready: Auto rollback configured and ready.

        Returns:
            ProductionGateResult with the gate outcome.
        """
        if self.config.skip_production:
            # Advance state machine even when skipping
            self.run.state = RunState.RUNNING_LEARNING
            self.run.current_gate = GateType.LEARNING
            return ProductionGateResult(
                deployed_to_production=False,
                verification_passed=False,
                rollback_ready=False,
                status=GateStatus.SKIPPED,
            )

        all_passed = deployed_to_production and verification_passed and rollback_ready
        status = GateStatus.PASSED if all_passed else GateStatus.FAILED

        result = ProductionGateResult(
            deployed_to_production=deployed_to_production,
            verification_passed=verification_passed,
            rollback_ready=rollback_ready,
            status=status,
        )

        if status == GateStatus.PASSED:
            self.run.state = RunState.RUNNING_LEARNING
            self.run.current_gate = GateType.LEARNING
        else:
            self._fail_run("Production gate failed")

        return result

    def execute_learning_gate(
        self,
        post_run_report_generated: bool = True,
        knowledge_artifacts_created: bool = True,
        suggestion_created: bool = False,
    ) -> LearningGateResult:
        """Execute the learning gate.

        Args:
            post_run_report_generated: Post-run report generated.
            knowledge_artifacts_created: Knowledge artifacts created.
            suggestion_created: Suggestion PR or issue created if improvements identified.

        Returns:
            LearningGateResult with the gate outcome.
        """
        # Learning gate has softer requirements - it passes as long as reports are created
        all_passed = post_run_report_generated and knowledge_artifacts_created
        status = GateStatus.PASSED if all_passed else GateStatus.FAILED

        result = LearningGateResult(
            post_run_report_generated=post_run_report_generated,
            knowledge_artifacts_created=knowledge_artifacts_created,
            suggestion_created=suggestion_created,
            status=status,
        )

        if status == GateStatus.PASSED:
            self._complete_run()
        else:
            self._fail_run("Learning gate failed")

        return result

    def block_run(self, reason: str) -> None:
        """Block the run for manual intervention.

        Args:
            reason: Reason why the run is blocked.
        """
        self.run.state = RunState.BLOCKED
        self.run.result = RunResult.BLOCKED
        self.run.blocked_reason = reason
        self.run.completed_at = datetime.now(timezone.utc)

    def _fail_run(self, message: str) -> None:
        """Mark the run as failed.

        Args:
            message: Error message describing the failure.
        """
        self.run.state = RunState.FAILED
        self.run.result = RunResult.FAILED
        self.run.error_message = message
        self.run.completed_at = datetime.now(timezone.utc)

    def _complete_run(self) -> None:
        """Mark the run as completed successfully."""
        self.run.state = RunState.COMPLETED
        self.run.result = RunResult.PASSED
        self.run.completed_at = datetime.now(timezone.utc)

    def build_pipeline(
        self,
        safety_result: SafetyGateResult,
        planning_result: PlanningGateResult,
        ci_result: CIGateResult,
        staging_result: StagingGateResult,
        production_result: ProductionGateResult,
        learning_result: LearningGateResult,
    ) -> GatePipeline:
        """Build a complete gate pipeline from individual results.

        Args:
            safety_result: Result from safety gate.
            planning_result: Result from planning gate.
            ci_result: Result from CI gate.
            staging_result: Result from staging gate.
            production_result: Result from production gate.
            learning_result: Result from learning gate.

        Returns:
            GatePipeline containing all gate results.
        """
        self.run.pipeline = GatePipeline(
            pr_number=self.config.pr_number,
            safety_gate=safety_result,
            planning_gate=planning_result,
            ci_gate=ci_result,
            staging_gate=staging_result,
            production_gate=production_result,
            learning_gate=learning_result,
        )
        return self.run.pipeline

    def execute_full_mock_run(self) -> GateRun:
        """Execute a complete mock run through all gates.

        This method runs through all gates with mock data (all passing)
        to demonstrate the state machine flow.

        Returns:
            The completed GateRun with all gate results.
        """
        if not self.config.mock_mode:
            raise ValueError("Full mock run requires mock_mode=True in config")

        self.start_run()

        # Execute all gates with passing mock data
        safety_result = self.execute_safety_gate()
        planning_result = self.execute_planning_gate()
        ci_result = self.execute_ci_gate()
        staging_result = self.execute_staging_gate()
        production_result = self.execute_production_gate()
        learning_result = self.execute_learning_gate()

        # Build complete pipeline
        self.build_pipeline(
            safety_result=safety_result,
            planning_result=planning_result,
            ci_result=ci_result,
            staging_result=staging_result,
            production_result=production_result,
            learning_result=learning_result,
        )

        return self.run


def create_mock_gate_run(pr_number: int, run_id: str) -> GateRun:
    """Create and execute a mock gate run.

    This is a convenience function for testing that a run can pass
    through all gates successfully.

    Args:
        pr_number: PR number to associate with the run.
        run_id: Unique identifier for this run.

    Returns:
        Completed GateRun with all passing gates.
    """
    config = GateRunConfig(
        pr_number=pr_number,
        run_id=run_id,
        mock_mode=True,
    )
    framework = GateFramework(config)
    return framework.execute_full_mock_run()
