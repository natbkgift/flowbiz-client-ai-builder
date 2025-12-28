"""Tests for Evidence Model v1."""

import time

import pytest

from packages.core.schemas.evidence import (
    CIEvidence,
    DeployEvidence,
    EvidenceChain,
    EvidenceSource,
    EvidenceType,
    PREvidence,
    VerifyEvidence,
)


class TestEvidence:
    def test_chain_add_and_summary(self):
        chain = EvidenceChain(run_id="run-001")

        pr_ev = PREvidence(
            evidence_id="e-pr-1",
            run_id="run-001",
            source=EvidenceSource.GITHUB,
            summary="PR opened",
            pr_number=123,
            pr_url="https://github.com/org/repo/pull/123",
        )
        ci_ev = CIEvidence(
            evidence_id="e-ci-1",
            run_id="run-001",
            source=EvidenceSource.CI_SYSTEM,
            summary="CI passed",
            workflow_name="CI",
            conclusion="success",
        )

        chain.add(pr_ev)
        chain.add(ci_ev)

        summary = chain.summary()
        assert summary["run_id"] == "run-001"
        assert summary["total"] == 2
        assert summary["by_type"] == {"pr": 1, "ci": 1}
        assert summary["latest_evidence_id"] in {"e-pr-1", "e-ci-1"}

    def test_chain_list_by_type(self):
        chain = EvidenceChain(run_id="run-002")
        chain.add(
            PREvidence(
                evidence_id="e1",
                run_id="run-002",
                source=EvidenceSource.GITHUB,
                summary="PR",
                pr_number=1,
            )
        )
        chain.add(
            PREvidence(
                evidence_id="e2",
                run_id="run-002",
                source=EvidenceSource.GITHUB,
                summary="PR update",
                pr_number=1,
            )
        )

        prs = chain.list_by_type(EvidenceType.PR)
        assert [e.evidence_id for e in prs] == ["e1", "e2"]

    def test_attach_artifact_dedupes(self):
        ev = PREvidence(
            evidence_id="e-pr-2",
            run_id="run-003",
            source=EvidenceSource.GITHUB,
            summary="PR",
            pr_number=2,
        )
        ev.attach_artifact("a-1")
        ev.attach_artifact("a-1")
        assert ev.artifact_ids == ["a-1"]

    def test_chain_rejects_wrong_run_id(self):
        chain = EvidenceChain(run_id="run-004")
        with pytest.raises(ValueError):
            chain.add(
                PREvidence(
                    evidence_id="e",
                    run_id="run-other",
                    source=EvidenceSource.GITHUB,
                    summary="bad",
                    pr_number=3,
                )
            )

    def test_deploy_evidence(self):
        """Test DeployEvidence can be created and added to chain."""
        chain = EvidenceChain(run_id="run-005")
        deploy_ev = DeployEvidence(
            evidence_id="e-deploy-1",
            run_id="run-005",
            source=EvidenceSource.CI_SYSTEM,
            summary="Deployed to staging",
            environment="staging",
            sha="abc123",
            status="success",
        )
        chain.add(deploy_ev)
        
        deploys = chain.list_by_type(EvidenceType.DEPLOY)
        assert len(deploys) == 1
        assert deploys[0].evidence_id == "e-deploy-1"
        assert deploys[0].environment == "staging"

    def test_verify_evidence(self):
        """Test VerifyEvidence can be created and added to chain."""
        chain = EvidenceChain(run_id="run-006")
        verify_ev = VerifyEvidence(
            evidence_id="e-verify-1",
            run_id="run-006",
            source=EvidenceSource.MANUAL,
            summary="Health check passed",
            check_name="smoke-test",
            passed=True,
            notes="All endpoints responding",
        )
        chain.add(verify_ev)
        
        verifies = chain.list_by_type(EvidenceType.VERIFY)
        assert len(verifies) == 1
        assert verifies[0].evidence_id == "e-verify-1"
        assert verifies[0].passed is True

    def test_chain_latest_returns_most_recent(self):
        """Test latest() method returns the most recent evidence."""
        chain = EvidenceChain(run_id="run-007")
        
        ev1 = PREvidence(
            evidence_id="e1",
            run_id="run-007",
            source=EvidenceSource.GITHUB,
            summary="First",
            pr_number=1,
        )
        chain.add(ev1)
        
        # Small delay to ensure different timestamps
        time.sleep(0.01)
        
        ev2 = CIEvidence(
            evidence_id="e2",
            run_id="run-007",
            source=EvidenceSource.CI_SYSTEM,
            summary="Second",
            workflow_name="CI",
        )
        chain.add(ev2)
        
        latest = chain.latest()
        assert latest is not None
        assert latest.evidence_id == "e2"

    def test_chain_latest_returns_none_when_empty(self):
        """Test latest() returns None for empty chain."""
        chain = EvidenceChain(run_id="run-008")
        assert chain.latest() is None
