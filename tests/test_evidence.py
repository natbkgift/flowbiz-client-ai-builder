"""Tests for Evidence Model.

Tests for PR #15 — Evidence Model + Artifact Registry v1.
BLUEPRINT_REF: PR #15 — Evidence Model + Artifact Registry v1
"""

from datetime import datetime, timezone

import pytest

from packages.core.schemas.evidence import (
    CIEvidence,
    DeployEvidence,
    Evidence,
    EvidenceChain,
    EvidenceSource,
    EvidenceType,
    GateEvidence,
    PREvidence,
    VerifyEvidence,
)


class TestEvidenceType:
    """Tests for EvidenceType enum."""

    def test_pr_evidence_types_exist(self):
        """PR evidence types should be defined."""
        assert EvidenceType.PR_CREATED == "pr_created"
        assert EvidenceType.PR_UPDATED == "pr_updated"
        assert EvidenceType.PR_MERGED == "pr_merged"
        assert EvidenceType.PR_CLOSED == "pr_closed"

    def test_ci_evidence_types_exist(self):
        """CI evidence types should be defined."""
        assert EvidenceType.CI_STARTED == "ci_started"
        assert EvidenceType.CI_PASSED == "ci_passed"
        assert EvidenceType.CI_FAILED == "ci_failed"

    def test_deploy_evidence_types_exist(self):
        """Deploy evidence types should be defined."""
        assert EvidenceType.DEPLOY_STARTED == "deploy_started"
        assert EvidenceType.DEPLOY_COMPLETED == "deploy_completed"
        assert EvidenceType.DEPLOY_FAILED == "deploy_failed"

    def test_verify_evidence_types_exist(self):
        """Verify evidence types should be defined."""
        assert EvidenceType.VERIFY_STARTED == "verify_started"
        assert EvidenceType.VERIFY_PASSED == "verify_passed"
        assert EvidenceType.VERIFY_FAILED == "verify_failed"

    def test_gate_evidence_types_exist(self):
        """Gate evidence types should be defined."""
        assert EvidenceType.GATE_PASSED == "gate_passed"
        assert EvidenceType.GATE_FAILED == "gate_failed"


class TestEvidenceSource:
    """Tests for EvidenceSource enum."""

    def test_all_sources_exist(self):
        """All evidence sources should be defined."""
        assert EvidenceSource.GITHUB_API == "github_api"
        assert EvidenceSource.GITHUB_WEBHOOK == "github_webhook"
        assert EvidenceSource.CI_WORKFLOW == "ci_workflow"
        assert EvidenceSource.DEPLOY_SCRIPT == "deploy_script"
        assert EvidenceSource.AGENT_ACTION == "agent_action"
        assert EvidenceSource.MANUAL_INPUT == "manual_input"
        assert EvidenceSource.SYSTEM_AUTO == "system_auto"


class TestEvidence:
    """Tests for base Evidence model."""

    def test_create_basic_evidence(self):
        """Should create basic evidence with required fields."""
        evidence = Evidence(
            evidence_id="ev-001",
            run_id="run-001",
            evidence_type=EvidenceType.PR_CREATED,
            source=EvidenceSource.GITHUB_API,
            actor="github-actions",
            summary="PR #123 created",
        )

        assert evidence.evidence_id == "ev-001"
        assert evidence.run_id == "run-001"
        assert evidence.evidence_type == EvidenceType.PR_CREATED
        assert evidence.source == EvidenceSource.GITHUB_API
        assert evidence.actor == "github-actions"
        assert evidence.summary == "PR #123 created"
        assert evidence.timestamp is not None

    def test_evidence_with_optional_fields(self):
        """Should create evidence with optional fields."""
        evidence = Evidence(
            evidence_id="ev-002",
            run_id="run-001",
            evidence_type=EvidenceType.CI_PASSED,
            source=EvidenceSource.CI_WORKFLOW,
            actor="ci-bot",
            summary="CI passed",
            details={"workflow": "ci.yml", "duration": 120},
            links=["https://github.com/org/repo/actions/runs/123"],
            pr_number=123,
            commit_sha="abc123",
            environment="staging",
        )

        assert evidence.details == {"workflow": "ci.yml", "duration": 120}
        assert len(evidence.links) == 1
        assert evidence.pr_number == 123
        assert evidence.commit_sha == "abc123"
        assert evidence.environment == "staging"

    def test_evidence_with_parent_reference(self):
        """Should support parent evidence reference."""
        evidence = Evidence(
            evidence_id="ev-003",
            run_id="run-001",
            evidence_type=EvidenceType.VERIFY_PASSED,
            source=EvidenceSource.DEPLOY_SCRIPT,
            actor="deploy-bot",
            summary="Verification passed",
            parent_evidence_id="ev-002",
        )

        assert evidence.parent_evidence_id == "ev-002"


class TestPREvidence:
    """Tests for PR-specific evidence."""

    def test_create_pr_evidence(self):
        """Should create PR evidence with PR-specific fields."""
        evidence = PREvidence(
            evidence_id="ev-pr-001",
            run_id="run-001",
            evidence_type=EvidenceType.PR_CREATED,
            source=EvidenceSource.GITHUB_API,
            actor="developer",
            summary="PR created for feature X",
            pr_number=123,
            pr_title="Add feature X",
            pr_url="https://github.com/org/repo/pull/123",
            base_branch="main",
            head_branch="feature/x",
            files_changed=5,
            additions=100,
            deletions=20,
        )

        assert evidence.pr_number == 123
        assert evidence.pr_title == "Add feature X"
        assert evidence.files_changed == 5
        assert evidence.additions == 100
        assert evidence.deletions == 20


class TestCIEvidence:
    """Tests for CI-specific evidence."""

    def test_create_ci_evidence(self):
        """Should create CI evidence with CI-specific fields."""
        evidence = CIEvidence(
            evidence_id="ev-ci-001",
            run_id="run-001",
            evidence_type=EvidenceType.CI_PASSED,
            source=EvidenceSource.CI_WORKFLOW,
            actor="github-actions",
            summary="CI workflow completed successfully",
            workflow_name="CI",
            workflow_run_id="12345",
            workflow_url="https://github.com/org/repo/actions/runs/12345",
            jobs_passed=4,
            jobs_failed=0,
            jobs_skipped=1,
            duration_seconds=180,
        )

        assert evidence.workflow_name == "CI"
        assert evidence.jobs_passed == 4
        assert evidence.jobs_failed == 0
        assert evidence.duration_seconds == 180

    def test_ci_evidence_with_failure(self):
        """Should record CI failure details."""
        evidence = CIEvidence(
            evidence_id="ev-ci-002",
            run_id="run-001",
            evidence_type=EvidenceType.CI_FAILED,
            source=EvidenceSource.CI_WORKFLOW,
            actor="github-actions",
            summary="CI workflow failed",
            workflow_name="CI",
            jobs_passed=2,
            jobs_failed=1,
            failure_reason="Test job failed: 3 tests failing",
        )

        assert evidence.jobs_failed == 1
        assert evidence.failure_reason == "Test job failed: 3 tests failing"


class TestDeployEvidence:
    """Tests for deployment evidence."""

    def test_create_deploy_evidence(self):
        """Should create deploy evidence with deploy-specific fields."""
        evidence = DeployEvidence(
            evidence_id="ev-deploy-001",
            run_id="run-001",
            evidence_type=EvidenceType.DEPLOY_COMPLETED,
            source=EvidenceSource.DEPLOY_SCRIPT,
            actor="deploy-bot",
            summary="Deployed to staging",
            environment="staging",
            deploy_sha="abc123def",
            deploy_version="1.2.0",
            previous_sha="xyz789abc",
            previous_version="1.1.0",
            deploy_duration_seconds=45,
            health_check_passed=True,
        )

        assert evidence.environment == "staging"
        assert evidence.deploy_sha == "abc123def"
        assert evidence.health_check_passed is True
        assert evidence.rollback_triggered is False

    def test_deploy_evidence_with_rollback(self):
        """Should record rollback information."""
        evidence = DeployEvidence(
            evidence_id="ev-deploy-002",
            run_id="run-001",
            evidence_type=EvidenceType.ROLLBACK_TRIGGERED,
            source=EvidenceSource.DEPLOY_SCRIPT,
            actor="deploy-bot",
            summary="Rollback triggered due to health check failure",
            environment="production",
            deploy_sha="abc123def",
            rollback_triggered=True,
            health_check_passed=False,
        )

        assert evidence.rollback_triggered is True
        assert evidence.health_check_passed is False


class TestVerifyEvidence:
    """Tests for verification evidence."""

    def test_create_verify_evidence(self):
        """Should create verify evidence with verification-specific fields."""
        evidence = VerifyEvidence(
            evidence_id="ev-verify-001",
            run_id="run-001",
            evidence_type=EvidenceType.VERIFY_PASSED,
            source=EvidenceSource.DEPLOY_SCRIPT,
            actor="verify-bot",
            summary="Smoke tests passed",
            environment="staging",
            verification_type="smoke",
            checks_passed=10,
            checks_failed=0,
            verification_duration_seconds=30,
        )

        assert evidence.verification_type == "smoke"
        assert evidence.checks_passed == 10
        assert evidence.checks_failed == 0

    def test_verify_evidence_with_failures(self):
        """Should record verification failures."""
        evidence = VerifyEvidence(
            evidence_id="ev-verify-002",
            run_id="run-001",
            evidence_type=EvidenceType.VERIFY_FAILED,
            source=EvidenceSource.DEPLOY_SCRIPT,
            actor="verify-bot",
            summary="Health check failed",
            environment="production",
            verification_type="health",
            checks_passed=2,
            checks_failed=1,
            failure_details="Database connection timeout",
        )

        assert evidence.checks_failed == 1
        assert evidence.failure_details == "Database connection timeout"


class TestGateEvidence:
    """Tests for gate evidence."""

    def test_create_gate_evidence_passed(self):
        """Should create gate evidence for passed gate."""
        evidence = GateEvidence(
            evidence_id="ev-gate-001",
            run_id="run-001",
            evidence_type=EvidenceType.GATE_PASSED,
            source=EvidenceSource.SYSTEM_AUTO,
            actor="gate-framework",
            summary="CI Gate passed",
            gate_type="ci",
            gate_result="passed",
            requirements_met=["lint_passed", "tests_passed", "security_scan_passed"],
        )

        assert evidence.gate_type == "ci"
        assert evidence.gate_result == "passed"
        assert len(evidence.requirements_met) == 3

    def test_create_gate_evidence_failed(self):
        """Should create gate evidence for failed gate."""
        evidence = GateEvidence(
            evidence_id="ev-gate-002",
            run_id="run-001",
            evidence_type=EvidenceType.GATE_FAILED,
            source=EvidenceSource.SYSTEM_AUTO,
            actor="gate-framework",
            summary="Planning Gate failed",
            gate_type="planning",
            gate_result="failed",
            blocking_reason="Missing test plan",
            requirements_met=["prd_provided"],
            requirements_missing=["test_plan_provided", "deploy_plan_provided"],
        )

        assert evidence.gate_type == "planning"
        assert evidence.gate_result == "failed"
        assert evidence.blocking_reason == "Missing test plan"
        assert len(evidence.requirements_missing) == 2


class TestEvidenceChain:
    """Tests for EvidenceChain model."""

    def test_create_empty_chain(self):
        """Should create empty evidence chain."""
        chain = EvidenceChain(
            chain_id="chain-001",
            run_id="run-001",
            pr_number=123,
            feature_name="Feature X",
        )

        assert chain.chain_id == "chain-001"
        assert chain.run_id == "run-001"
        assert len(chain.evidence_items) == 0
        assert chain.current_status == "in_progress"

    def test_add_evidence_to_chain(self):
        """Should add evidence to chain."""
        chain = EvidenceChain(chain_id="chain-001", run_id="run-001")

        evidence = Evidence(
            evidence_id="ev-001",
            run_id="run-001",
            evidence_type=EvidenceType.PR_CREATED,
            source=EvidenceSource.GITHUB_API,
            actor="developer",
            summary="PR created",
        )

        chain.add_evidence(evidence)

        assert len(chain.evidence_items) == 1
        assert chain.evidence_items[0].evidence_id == "ev-001"

    def test_get_evidence_by_type(self):
        """Should filter evidence by type."""
        chain = EvidenceChain(chain_id="chain-001", run_id="run-001")

        chain.add_evidence(
            Evidence(
                evidence_id="ev-001",
                run_id="run-001",
                evidence_type=EvidenceType.PR_CREATED,
                source=EvidenceSource.GITHUB_API,
                actor="dev",
                summary="PR created",
            )
        )
        chain.add_evidence(
            Evidence(
                evidence_id="ev-002",
                run_id="run-001",
                evidence_type=EvidenceType.CI_PASSED,
                source=EvidenceSource.CI_WORKFLOW,
                actor="ci",
                summary="CI passed",
            )
        )
        chain.add_evidence(
            Evidence(
                evidence_id="ev-003",
                run_id="run-001",
                evidence_type=EvidenceType.CI_FAILED,
                source=EvidenceSource.CI_WORKFLOW,
                actor="ci",
                summary="CI failed",
            )
        )

        pr_evidence = chain.get_evidence_by_type(EvidenceType.PR_CREATED)
        assert len(pr_evidence) == 1

        ci_passed = chain.get_evidence_by_type(EvidenceType.CI_PASSED)
        assert len(ci_passed) == 1

    def test_get_latest_evidence(self):
        """Should return most recent evidence."""
        chain = EvidenceChain(chain_id="chain-001", run_id="run-001")

        # Empty chain
        assert chain.get_latest_evidence() is None

        # Add evidence
        ev1 = Evidence(
            evidence_id="ev-001",
            run_id="run-001",
            evidence_type=EvidenceType.PR_CREATED,
            source=EvidenceSource.GITHUB_API,
            actor="dev",
            summary="First",
            timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
        ev2 = Evidence(
            evidence_id="ev-002",
            run_id="run-001",
            evidence_type=EvidenceType.CI_PASSED,
            source=EvidenceSource.CI_WORKFLOW,
            actor="ci",
            summary="Second",
            timestamp=datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc),
        )

        chain.add_evidence(ev1)
        chain.add_evidence(ev2)

        latest = chain.get_latest_evidence()
        assert latest is not None
        assert latest.evidence_id == "ev-002"

    def test_get_evidence_summary(self):
        """Should generate summary of evidence."""
        chain = EvidenceChain(chain_id="chain-001", run_id="run-001")

        chain.add_evidence(
            Evidence(
                evidence_id="ev-001",
                run_id="run-001",
                evidence_type=EvidenceType.PR_CREATED,
                source=EvidenceSource.GITHUB_API,
                actor="dev",
                summary="PR created",
            )
        )
        chain.add_evidence(
            Evidence(
                evidence_id="ev-002",
                run_id="run-001",
                evidence_type=EvidenceType.CI_PASSED,
                source=EvidenceSource.CI_WORKFLOW,
                actor="ci",
                summary="CI passed",
            )
        )

        summary = chain.get_evidence_summary()

        assert summary["total_evidence_count"] == 2
        assert "pr_created" in summary["evidence_by_type"]
        assert "ci_passed" in summary["evidence_by_type"]
        assert summary["has_failures"] is False
        assert summary["latest_action"] is not None

    def test_evidence_summary_detects_failures(self):
        """Should detect failures in summary."""
        chain = EvidenceChain(chain_id="chain-001", run_id="run-001")

        chain.add_evidence(
            Evidence(
                evidence_id="ev-001",
                run_id="run-001",
                evidence_type=EvidenceType.CI_FAILED,
                source=EvidenceSource.CI_WORKFLOW,
                actor="ci",
                summary="CI failed",
            )
        )

        summary = chain.get_evidence_summary()
        assert summary["has_failures"] is True

    def test_is_complete_for_merged_pr(self):
        """Should detect completed chain via PR merged."""
        chain = EvidenceChain(chain_id="chain-001", run_id="run-001")

        assert chain.is_complete() is False

        chain.add_evidence(
            Evidence(
                evidence_id="ev-001",
                run_id="run-001",
                evidence_type=EvidenceType.PR_MERGED,
                source=EvidenceSource.GITHUB_WEBHOOK,
                actor="merge-bot",
                summary="PR merged",
            )
        )

        assert chain.is_complete() is True

    def test_is_complete_for_closed_pr(self):
        """Should detect completed chain via PR closed."""
        chain = EvidenceChain(chain_id="chain-001", run_id="run-001")

        chain.add_evidence(
            Evidence(
                evidence_id="ev-001",
                run_id="run-001",
                evidence_type=EvidenceType.PR_CLOSED,
                source=EvidenceSource.GITHUB_WEBHOOK,
                actor="author",
                summary="PR closed without merge",
            )
        )

        assert chain.is_complete() is True

    def test_mark_complete(self):
        """Should mark chain as complete."""
        chain = EvidenceChain(chain_id="chain-001", run_id="run-001")

        assert chain.completed_at is None
        assert chain.current_status == "in_progress"

        chain.mark_complete("success")

        assert chain.completed_at is not None
        assert chain.current_status == "success"
