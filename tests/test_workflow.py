"""Tests for workflow schemas."""

from packages.core.schemas.workflow import (
    ApprovalRequired,
    AutoApprovalConfig,
    BuildPhaseOutput,
    DiscoveryPhaseOutput,
    HotfixWorkflow,
    LearnPhaseOutput,
    PlanPhaseOutput,
    PRWorkflow,
    ReleasePhaseOutput,
    WorkflowExecution,
    WorkflowPhase,
    WorkflowStatus,
)


def test_pr_workflow_creation():
    """Test PR workflow creation."""
    workflow = PRWorkflow(
        workflow_id="wf-001",
        branch_name="feature/performance",
        phase=WorkflowPhase.BUILD,
        status=WorkflowStatus.IN_PROGRESS,
    )
    assert workflow.workflow_id == "wf-001"
    assert workflow.phase == WorkflowPhase.BUILD
    assert workflow.status == WorkflowStatus.IN_PROGRESS


def test_discovery_phase_output():
    """Test discovery phase output."""
    output = DiscoveryPhaseOutput(
        requirements_gathered=True,
        problem_statement="Improve API performance",
        stakeholders_identified=["Product", "Engineering"],
        constraints=["Backward compatibility required"],
    )
    assert output.requirements_gathered is True
    assert len(output.stakeholders_identified) == 2


def test_plan_phase_output():
    """Test plan phase output."""
    output = PlanPhaseOutput(
        squad_assembled=True,
        acceptance_criteria_defined=True,
        test_plan_created=True,
        deployment_plan_created=True,
        scope_locked=True,
    )
    assert output.squad_assembled is True
    assert output.scope_locked is True


def test_build_phase_output():
    """Test build phase output."""
    output = BuildPhaseOutput(
        code_written=True,
        tests_written=True,
        code_reviewed=True,
        security_reviewed=True,
        documentation_updated=True,
    )
    assert output.code_written is True
    assert output.security_reviewed is True


def test_release_phase_output():
    """Test release phase output."""
    output = ReleasePhaseOutput(
        deployed_to_staging=True,
        staging_verified=True,
        deployed_to_production=True,
        production_verified=True,
        rollback_tested=True,
    )
    assert output.deployed_to_staging is True
    assert output.production_verified is True


def test_learn_phase_output():
    """Test learn phase output."""
    output = LearnPhaseOutput(
        knowledge_artifacts_created=True,
        metrics_collected=True,
        improvements_identified=True,
        automation_opportunities_documented=True,
    )
    assert output.knowledge_artifacts_created is True
    assert output.automation_opportunities_documented is True


def test_workflow_execution():
    """Test workflow execution."""
    execution = WorkflowExecution(
        workflow_id="wf-001",
        pr_number=123,
        squad_id="squad-001",
        feature_name="Performance optimization",
        current_phase=WorkflowPhase.BUILD,
        status=WorkflowStatus.IN_PROGRESS,
    )
    assert execution.pr_number == 123
    assert execution.current_phase == WorkflowPhase.BUILD


def test_approval_required():
    """Test approval required."""
    approval = ApprovalRequired(
        approval_id="appr-001",
        workflow_id="wf-001",
        reason="Breaking API change",
        approval_type="breaking_api",
    )
    assert approval.approval_id == "appr-001"
    assert approval.approved is None


def test_hotfix_workflow():
    """Test hotfix workflow."""
    hotfix = HotfixWorkflow(
        hotfix_id="hotfix-001",
        original_pr_number=123,
        issue_description="CI check failed",
        triggered_by="policy-check",
        status=WorkflowStatus.PENDING,
    )
    assert hotfix.original_pr_number == 123
    assert hotfix.triggered_by == "policy-check"


def test_workflow_phase_enum():
    """Test workflow phase enum values."""
    assert WorkflowPhase.DISCOVERY == "discovery"
    assert WorkflowPhase.PLAN == "plan"
    assert WorkflowPhase.BUILD == "build"
    assert WorkflowPhase.RELEASE == "release"
    assert WorkflowPhase.LEARN == "learn"


def test_workflow_status_enum():
    """Test workflow status enum values."""
    assert WorkflowStatus.PENDING == "pending"
    assert WorkflowStatus.IN_PROGRESS == "in_progress"
    assert WorkflowStatus.COMPLETED == "completed"


def test_approval_auto_approve_disabled():
    """Test that auto-approval doesn't work when disabled."""
    approval = ApprovalRequired(
        approval_id="appr-002",
        workflow_id="wf-002",
        reason="Environment deployment",
        approval_type="environment_approval",
        auto_approve_enabled=False,
    )

    approval.auto_approve()

    # Should not be approved because auto_approve_enabled is False
    assert approval.approved is None
    assert approval.approved_by is None
    assert approval.approved_at is None


def test_approval_auto_approve_enabled():
    """Test that auto-approval works when enabled."""
    approval = ApprovalRequired(
        approval_id="appr-003",
        workflow_id="wf-003",
        reason="Workflow approval",
        approval_type="workflow_approval",
        auto_approve_enabled=True,
    )

    approval.auto_approve()

    # Should be approved
    assert approval.approved is True
    assert approval.approved_by == "system"
    assert approval.approved_at is not None
    assert approval.comments == "Auto-approved by system"


def test_approval_auto_approve_with_custom_approver():
    """Test auto-approval with a custom approver name."""
    approval = ApprovalRequired(
        approval_id="appr-004",
        workflow_id="wf-004",
        reason="Workflow approval",
        approval_type="workflow_approval",
        auto_approve_enabled=True,
    )

    approval.auto_approve(approver="ci-bot")

    assert approval.approved is True
    assert approval.approved_by == "ci-bot"
    assert approval.comments == "Auto-approved by ci-bot"


def test_auto_approval_config_disabled():
    """Test auto-approval config when globally disabled."""
    config = AutoApprovalConfig(enabled=False)

    approval = ApprovalRequired(
        approval_id="appr-005",
        workflow_id="wf-005",
        reason="Test approval",
        approval_type="workflow_approval",
    )

    assert config.can_auto_approve(approval, ci_passed=True) is False


def test_auto_approval_config_enabled():
    """Test auto-approval config when enabled with matching type."""
    config = AutoApprovalConfig(
        enabled=True,
        approval_types=["workflow_approval", "environment_approval"],
        require_ci_pass=True,
    )

    approval = ApprovalRequired(
        approval_id="appr-006",
        workflow_id="wf-006",
        reason="Test approval",
        approval_type="workflow_approval",
    )

    # Should allow auto-approval when CI passed
    assert config.can_auto_approve(approval, ci_passed=True) is True

    # Should not allow when CI hasn't passed
    assert config.can_auto_approve(approval, ci_passed=False) is False


def test_auto_approval_config_excluded_workflow():
    """Test that excluded workflows cannot be auto-approved."""
    config = AutoApprovalConfig(
        enabled=True,
        approval_types=["workflow_approval"],
        excluded_workflows=["wf-007"],
    )

    approval = ApprovalRequired(
        approval_id="appr-007",
        workflow_id="wf-007",
        reason="Test approval",
        approval_type="workflow_approval",
    )

    # Should not allow because workflow is excluded
    assert config.can_auto_approve(approval, ci_passed=True) is False


def test_auto_approval_config_wrong_type():
    """Test that approvals with non-whitelisted types cannot be auto-approved."""
    config = AutoApprovalConfig(
        enabled=True,
        approval_types=["workflow_approval"],
        require_ci_pass=True,
    )

    approval = ApprovalRequired(
        approval_id="appr-008",
        workflow_id="wf-008",
        reason="Breaking API change",
        approval_type="breaking_api",
    )

    # Should not allow because breaking_api is not in approval_types
    assert config.can_auto_approve(approval, ci_passed=True) is False


def test_auto_approval_config_no_ci_requirement():
    """Test auto-approval config when CI pass is not required."""
    config = AutoApprovalConfig(
        enabled=True,
        approval_types=["workflow_approval"],
        require_ci_pass=False,
    )

    approval = ApprovalRequired(
        approval_id="appr-009",
        workflow_id="wf-009",
        reason="Test approval",
        approval_type="workflow_approval",
    )

    # Should allow auto-approval even when CI hasn't passed
    assert config.can_auto_approve(approval, ci_passed=False) is True
    assert config.can_auto_approve(approval, ci_passed=True) is True
