"""Tests for gate schemas."""

from packages.core.schemas.gates import (
    CIGateResult,
    GatePipeline,
    GateStatus,
    LearningGateResult,
    PlanningGateResult,
    ProductionGateResult,
    SafetyGateResult,
    StagingGateResult,
)


def test_safety_gate_result():
    """Test safety gate result creation."""
    result = SafetyGateResult(
        forbidden_paths_checked=True,
        secrets_checked=True,
        permissions_valid=True,
        status=GateStatus.PASSED,
    )
    assert result.forbidden_paths_checked is True
    assert result.status == GateStatus.PASSED


def test_planning_gate_result():
    """Test planning gate result creation."""
    result = PlanningGateResult(
        prd_provided=True,
        test_plan_provided=True,
        deploy_plan_provided=True,
        status=GateStatus.PASSED,
    )
    assert result.prd_provided is True
    assert result.status == GateStatus.PASSED


def test_ci_gate_result():
    """Test CI gate result creation."""
    result = CIGateResult(
        lint_passed=True,
        unit_tests_passed=True,
        security_scan_passed=True,
        dependency_check_passed=True,
        status=GateStatus.PASSED,
    )
    assert result.lint_passed is True
    assert result.status == GateStatus.PASSED


def test_staging_gate_result():
    """Test staging gate result creation."""
    result = StagingGateResult(
        deployed_to_staging=True,
        smoke_tests_passed=True,
        evidence_attached=True,
        status=GateStatus.PASSED,
    )
    assert result.deployed_to_staging is True
    assert result.status == GateStatus.PASSED


def test_production_gate_result():
    """Test production gate result creation."""
    result = ProductionGateResult(
        deployed_to_production=True,
        verification_passed=True,
        rollback_ready=True,
        status=GateStatus.PASSED,
    )
    assert result.deployed_to_production is True
    assert result.status == GateStatus.PASSED


def test_learning_gate_result():
    """Test learning gate result creation."""
    result = LearningGateResult(
        post_run_report_generated=True,
        knowledge_artifacts_created=True,
        suggestion_created=False,
        status=GateStatus.PASSED,
    )
    assert result.post_run_report_generated is True
    assert result.suggestion_created is False


def test_gate_pipeline_is_ready_for_merge():
    """Test gate pipeline ready for merge check."""
    pipeline = GatePipeline(
        pr_number=123,
        safety_gate=SafetyGateResult(
            forbidden_paths_checked=True,
            secrets_checked=True,
            permissions_valid=True,
            status=GateStatus.PASSED,
        ),
        planning_gate=PlanningGateResult(
            prd_provided=True,
            test_plan_provided=True,
            deploy_plan_provided=True,
            status=GateStatus.PASSED,
        ),
        ci_gate=CIGateResult(
            lint_passed=True,
            unit_tests_passed=True,
            security_scan_passed=True,
            dependency_check_passed=True,
            status=GateStatus.PASSED,
        ),
        staging_gate=StagingGateResult(
            deployed_to_staging=False,
            smoke_tests_passed=False,
            evidence_attached=False,
            status=GateStatus.PENDING,
        ),
        production_gate=ProductionGateResult(
            deployed_to_production=False,
            verification_passed=False,
            rollback_ready=False,
            status=GateStatus.PENDING,
        ),
        learning_gate=LearningGateResult(
            post_run_report_generated=False,
            knowledge_artifacts_created=False,
            status=GateStatus.PENDING,
        ),
    )
    assert pipeline.is_ready_for_merge() is True
    assert pipeline.is_production_ready() is False


def test_gate_pipeline_is_production_ready():
    """Test gate pipeline production ready check."""
    pipeline = GatePipeline(
        pr_number=123,
        safety_gate=SafetyGateResult(
            forbidden_paths_checked=True,
            secrets_checked=True,
            permissions_valid=True,
            status=GateStatus.PASSED,
        ),
        planning_gate=PlanningGateResult(
            prd_provided=True,
            test_plan_provided=True,
            deploy_plan_provided=True,
            status=GateStatus.PASSED,
        ),
        ci_gate=CIGateResult(
            lint_passed=True,
            unit_tests_passed=True,
            security_scan_passed=True,
            dependency_check_passed=True,
            status=GateStatus.PASSED,
        ),
        staging_gate=StagingGateResult(
            deployed_to_staging=True,
            smoke_tests_passed=True,
            evidence_attached=True,
            status=GateStatus.PASSED,
        ),
        production_gate=ProductionGateResult(
            deployed_to_production=True,
            verification_passed=True,
            rollback_ready=True,
            status=GateStatus.PASSED,
        ),
        learning_gate=LearningGateResult(
            post_run_report_generated=False,
            knowledge_artifacts_created=False,
            status=GateStatus.PENDING,
        ),
    )
    assert pipeline.is_ready_for_merge() is True
    assert pipeline.is_production_ready() is True
