"""Tests for Gate Framework v1."""

import pytest

from packages.core.gate_framework import (
    GateFramework,
    GateRunConfig,
    RunResult,
    RunState,
    create_mock_gate_run,
)
from packages.core.schemas.gates import GateStatus, GateType


class TestGateFramework:
    """Tests for the GateFramework class."""

    def test_framework_initialization(self):
        """Test framework initializes correctly."""
        config = GateRunConfig(
            pr_number=123,
            run_id="test-run-001",
            mock_mode=True,
        )
        framework = GateFramework(config)

        assert framework.run.run_id == "test-run-001"
        assert framework.run.pr_number == 123
        assert framework.run.state == RunState.INITIALIZED
        assert framework.run.result == RunResult.PENDING

    def test_start_run(self):
        """Test starting a run transitions to safety gate."""
        config = GateRunConfig(
            pr_number=123,
            run_id="test-run-002",
            mock_mode=True,
        )
        framework = GateFramework(config)
        run = framework.start_run()

        assert run.state == RunState.RUNNING_SAFETY
        assert run.current_gate == GateType.SAFETY

    def test_safety_gate_pass(self):
        """Test safety gate passing."""
        config = GateRunConfig(
            pr_number=123,
            run_id="test-run-003",
            mock_mode=True,
        )
        framework = GateFramework(config)
        framework.start_run()

        result = framework.execute_safety_gate(
            forbidden_paths_checked=True,
            secrets_checked=True,
            permissions_valid=True,
        )

        assert result.status == GateStatus.PASSED
        assert framework.run.state == RunState.RUNNING_PLANNING
        assert framework.run.current_gate == GateType.PLANNING

    def test_safety_gate_fail(self):
        """Test safety gate failing."""
        config = GateRunConfig(
            pr_number=123,
            run_id="test-run-004",
            mock_mode=True,
        )
        framework = GateFramework(config)
        framework.start_run()

        result = framework.execute_safety_gate(
            forbidden_paths_checked=True,
            secrets_checked=False,  # Secret leak!
            permissions_valid=True,
        )

        assert result.status == GateStatus.FAILED
        assert framework.run.state == RunState.FAILED
        assert framework.run.result == RunResult.FAILED
        assert "Safety gate failed" in framework.run.error_message

    def test_planning_gate_pass(self):
        """Test planning gate passing."""
        config = GateRunConfig(
            pr_number=123,
            run_id="test-run-005",
            mock_mode=True,
        )
        framework = GateFramework(config)
        framework.start_run()
        framework.execute_safety_gate()

        result = framework.execute_planning_gate(
            prd_provided=True,
            test_plan_provided=True,
            deploy_plan_provided=True,
        )

        assert result.status == GateStatus.PASSED
        assert framework.run.state == RunState.RUNNING_CI
        assert framework.run.current_gate == GateType.CI

    def test_planning_gate_fail(self):
        """Test planning gate failing."""
        config = GateRunConfig(
            pr_number=123,
            run_id="test-run-006",
            mock_mode=True,
        )
        framework = GateFramework(config)
        framework.start_run()
        framework.execute_safety_gate()

        result = framework.execute_planning_gate(
            prd_provided=True,
            test_plan_provided=False,  # No test plan!
            deploy_plan_provided=True,
        )

        assert result.status == GateStatus.FAILED
        assert framework.run.state == RunState.FAILED

    def test_ci_gate_pass(self):
        """Test CI gate passing."""
        config = GateRunConfig(
            pr_number=123,
            run_id="test-run-007",
            mock_mode=True,
        )
        framework = GateFramework(config)
        framework.start_run()
        framework.execute_safety_gate()
        framework.execute_planning_gate()

        result = framework.execute_ci_gate(
            lint_passed=True,
            unit_tests_passed=True,
            security_scan_passed=True,
            dependency_check_passed=True,
        )

        assert result.status == GateStatus.PASSED
        assert framework.run.state == RunState.RUNNING_STAGING

    def test_ci_gate_fail(self):
        """Test CI gate failing."""
        config = GateRunConfig(
            pr_number=123,
            run_id="test-run-008",
            mock_mode=True,
        )
        framework = GateFramework(config)
        framework.start_run()
        framework.execute_safety_gate()
        framework.execute_planning_gate()

        result = framework.execute_ci_gate(
            lint_passed=True,
            unit_tests_passed=False,  # Tests failed!
            security_scan_passed=True,
            dependency_check_passed=True,
        )

        assert result.status == GateStatus.FAILED
        assert framework.run.state == RunState.FAILED

    def test_staging_gate_pass(self):
        """Test staging gate passing."""
        config = GateRunConfig(
            pr_number=123,
            run_id="test-run-009",
            mock_mode=True,
        )
        framework = GateFramework(config)
        framework.start_run()
        framework.execute_safety_gate()
        framework.execute_planning_gate()
        framework.execute_ci_gate()

        result = framework.execute_staging_gate(
            deployed_to_staging=True,
            smoke_tests_passed=True,
            evidence_attached=True,
        )

        assert result.status == GateStatus.PASSED
        assert framework.run.state == RunState.RUNNING_PRODUCTION

    def test_staging_gate_skipped(self):
        """Test staging gate being skipped."""
        config = GateRunConfig(
            pr_number=123,
            run_id="test-run-010",
            mock_mode=True,
            skip_staging=True,
        )
        framework = GateFramework(config)
        framework.start_run()
        framework.execute_safety_gate()
        framework.execute_planning_gate()
        framework.execute_ci_gate()

        # CI gate should skip directly to production
        assert framework.run.state == RunState.RUNNING_PRODUCTION

        result = framework.execute_staging_gate()
        assert result.status == GateStatus.SKIPPED

    def test_production_gate_pass(self):
        """Test production gate passing."""
        config = GateRunConfig(
            pr_number=123,
            run_id="test-run-011",
            mock_mode=True,
        )
        framework = GateFramework(config)
        framework.start_run()
        framework.execute_safety_gate()
        framework.execute_planning_gate()
        framework.execute_ci_gate()
        framework.execute_staging_gate()

        result = framework.execute_production_gate(
            deployed_to_production=True,
            verification_passed=True,
            rollback_ready=True,
        )

        assert result.status == GateStatus.PASSED
        assert framework.run.state == RunState.RUNNING_LEARNING

    def test_production_gate_skipped(self):
        """Test production gate being skipped."""
        config = GateRunConfig(
            pr_number=123,
            run_id="test-run-012",
            mock_mode=True,
            skip_production=True,
        )
        framework = GateFramework(config)
        framework.start_run()
        framework.execute_safety_gate()
        framework.execute_planning_gate()
        framework.execute_ci_gate()
        framework.execute_staging_gate()

        # Staging should skip directly to learning
        assert framework.run.state == RunState.RUNNING_LEARNING

        result = framework.execute_production_gate()
        assert result.status == GateStatus.SKIPPED

    def test_learning_gate_pass(self):
        """Test learning gate passing."""
        config = GateRunConfig(
            pr_number=123,
            run_id="test-run-013",
            mock_mode=True,
        )
        framework = GateFramework(config)
        framework.start_run()
        framework.execute_safety_gate()
        framework.execute_planning_gate()
        framework.execute_ci_gate()
        framework.execute_staging_gate()
        framework.execute_production_gate()

        result = framework.execute_learning_gate(
            post_run_report_generated=True,
            knowledge_artifacts_created=True,
            suggestion_created=False,
        )

        assert result.status == GateStatus.PASSED
        assert framework.run.state == RunState.COMPLETED
        assert framework.run.result == RunResult.PASSED
        assert framework.run.completed_at is not None

    def test_learning_gate_fail(self):
        """Test learning gate failing."""
        config = GateRunConfig(
            pr_number=123,
            run_id="test-run-014",
            mock_mode=True,
        )
        framework = GateFramework(config)
        framework.start_run()
        framework.execute_safety_gate()
        framework.execute_planning_gate()
        framework.execute_ci_gate()
        framework.execute_staging_gate()
        framework.execute_production_gate()

        result = framework.execute_learning_gate(
            post_run_report_generated=False,  # No report!
            knowledge_artifacts_created=False,
            suggestion_created=False,
        )

        assert result.status == GateStatus.FAILED
        assert framework.run.state == RunState.FAILED

    def test_block_run(self):
        """Test blocking a run."""
        config = GateRunConfig(
            pr_number=123,
            run_id="test-run-015",
            mock_mode=True,
        )
        framework = GateFramework(config)
        framework.start_run()

        framework.block_run("Awaiting human approval")

        assert framework.run.state == RunState.BLOCKED
        assert framework.run.result == RunResult.BLOCKED
        assert framework.run.blocked_reason == "Awaiting human approval"
        assert framework.run.completed_at is not None


class TestFullMockRun:
    """Tests for full mock run functionality."""

    def test_execute_full_mock_run(self):
        """Test executing a full mock run through all gates."""
        config = GateRunConfig(
            pr_number=123,
            run_id="test-full-001",
            mock_mode=True,
        )
        framework = GateFramework(config)
        run = framework.execute_full_mock_run()

        assert run.state == RunState.COMPLETED
        assert run.result == RunResult.PASSED
        assert run.pipeline is not None
        assert run.pipeline.is_ready_for_merge() is True
        assert run.pipeline.is_production_ready() is True

    def test_execute_full_mock_run_requires_mock_mode(self):
        """Test that full mock run requires mock_mode=True."""
        config = GateRunConfig(
            pr_number=123,
            run_id="test-full-002",
            mock_mode=False,
        )
        framework = GateFramework(config)

        with pytest.raises(ValueError, match="mock_mode=True"):
            framework.execute_full_mock_run()


class TestConvenienceFunction:
    """Tests for the create_mock_gate_run convenience function."""

    def test_create_mock_gate_run(self):
        """Test convenience function creates successful run."""
        run = create_mock_gate_run(pr_number=456, run_id="convenience-001")

        assert run.pr_number == 456
        assert run.run_id == "convenience-001"
        assert run.state == RunState.COMPLETED
        assert run.result == RunResult.PASSED
        assert run.pipeline is not None
        assert run.pipeline.is_ready_for_merge() is True


class TestProgressPercentage:
    """Tests for progress percentage calculation."""

    def test_progress_initialized(self):
        """Test progress percentage at initialization."""
        config = GateRunConfig(pr_number=123, run_id="progress-001")
        framework = GateFramework(config)

        assert framework.run.get_progress_percentage() == 0

    def test_progress_running_safety(self):
        """Test progress percentage during safety gate."""
        config = GateRunConfig(pr_number=123, run_id="progress-002")
        framework = GateFramework(config)
        framework.start_run()

        assert framework.run.get_progress_percentage() == 10

    def test_progress_completed(self):
        """Test progress percentage at completion."""
        run = create_mock_gate_run(pr_number=123, run_id="progress-003")

        assert run.get_progress_percentage() == 100

    def test_progress_failed(self):
        """Test progress percentage when failed."""
        config = GateRunConfig(pr_number=123, run_id="progress-004")
        framework = GateFramework(config)
        framework.start_run()
        framework.execute_safety_gate(secrets_checked=False)

        assert framework.run.get_progress_percentage() == -1


class TestStateMachineTransitions:
    """Tests for state machine transitions."""

    def test_complete_state_machine_flow(self):
        """Test complete state machine flow through all states."""
        config = GateRunConfig(pr_number=123, run_id="flow-001", mock_mode=True)
        framework = GateFramework(config)

        # Track state transitions
        states = [framework.run.state]

        framework.start_run()
        states.append(framework.run.state)

        framework.execute_safety_gate()
        states.append(framework.run.state)

        framework.execute_planning_gate()
        states.append(framework.run.state)

        framework.execute_ci_gate()
        states.append(framework.run.state)

        framework.execute_staging_gate()
        states.append(framework.run.state)

        framework.execute_production_gate()
        states.append(framework.run.state)

        framework.execute_learning_gate()
        states.append(framework.run.state)

        expected_states = [
            RunState.INITIALIZED,
            RunState.RUNNING_SAFETY,
            RunState.RUNNING_PLANNING,
            RunState.RUNNING_CI,
            RunState.RUNNING_STAGING,
            RunState.RUNNING_PRODUCTION,
            RunState.RUNNING_LEARNING,
            RunState.COMPLETED,
        ]

        assert states == expected_states

    def test_state_machine_flow_with_skips(self):
        """Test state machine flow with staging and production skipped."""
        config = GateRunConfig(
            pr_number=123,
            run_id="flow-002",
            mock_mode=True,
            skip_staging=True,
            skip_production=True,
        )
        framework = GateFramework(config)

        # Track state transitions
        states = [framework.run.state]

        framework.start_run()
        states.append(framework.run.state)

        framework.execute_safety_gate()
        states.append(framework.run.state)

        framework.execute_planning_gate()
        states.append(framework.run.state)

        framework.execute_ci_gate()
        states.append(framework.run.state)
        # At this point, CI should skip directly to production when skip_staging=True

        framework.execute_staging_gate()  # Will return SKIPPED, state already at production
        framework.execute_production_gate()  # Will return SKIPPED
        states.append(framework.run.state)
        # At this point, production should skip to learning when skip_production=True

        framework.execute_learning_gate()
        states.append(framework.run.state)

        expected_states = [
            RunState.INITIALIZED,
            RunState.RUNNING_SAFETY,
            RunState.RUNNING_PLANNING,
            RunState.RUNNING_CI,
            RunState.RUNNING_PRODUCTION,  # CI skipped to production (staging skipped)
            RunState.RUNNING_LEARNING,  # Production gate moved to learning
            RunState.COMPLETED,
        ]

        assert states == expected_states
