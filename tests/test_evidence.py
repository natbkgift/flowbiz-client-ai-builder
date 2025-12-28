"""Tests for Evidence Model v1."""

import pytest

from packages.core.schemas.evidence import (
    CIEvidence,
    DeployEvidence,
    EvidenceChain,
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
            source="github",
            summary="PR opened",
            pr_number=123,
            pr_url="https://github.com/org/repo/pull/123",
        )
        ci_ev = CIEvidence(
            evidence_id="e-ci-1",
            run_id="run-001",
            source="ci_system",
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
                source="github",
                summary="PR",
                pr_number=1,
            )
        )
        chain.add(
            PREvidence(
                evidence_id="e2",
                run_id="run-002",
                source="github",
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
            source="github",
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
                    source="github",
                    summary="bad",
                    pr_number=3,
                )
            )

    def test_deploy_evidence(self):
        chain = EvidenceChain(run_id="run-005")
        deploy_ev = DeployEvidence(
            evidence_id="e-deploy-1",
            run_id="run-005",
            source="ci_system",
            summary="Deployed to staging",
            environment="staging",
            sha="abc123",
            status="success",
        )
        chain.add(deploy_ev)

        summary = chain.summary()
        assert summary["run_id"] == "run-005"
        assert summary["total"] == 1
        assert summary["by_type"] == {"deploy": 1}
        assert summary["latest_evidence_id"] == "e-deploy-1"

    def test_verify_evidence(self):
        chain = EvidenceChain(run_id="run-006")
        verify_ev = VerifyEvidence(
            evidence_id="e-verify-1",
            run_id="run-006",
            source="ci_system",
            summary="Security scan passed",
            check_name="security-scan",
            passed=True,
            notes="No vulnerabilities found",
        )
        chain.add(verify_ev)

        summary = chain.summary()
        assert summary["run_id"] == "run-006"
        assert summary["total"] == 1
        assert summary["by_type"] == {"verify": 1}
        assert summary["latest_evidence_id"] == "e-verify-1"
