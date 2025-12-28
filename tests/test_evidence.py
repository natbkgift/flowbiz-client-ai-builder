"""Tests for Evidence Model v1."""

import pytest

from packages.core.schemas.evidence import (
    CIEvidence,
    EvidenceChain,
    EvidenceType,
    PREvidence,
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
"""Tests for Evidence Model v1."""

import pytest

from packages.core.schemas.evidence import (
<<<<<<< HEAD
    ArtifactType,
    EvidenceRegistry,
    EvidenceStatus,
    EvidenceType,
)


class TestArtifactRegistration:
    """Tests for registering artifacts."""

    def test_register_file_and_link_artifacts(self):
        registry = EvidenceRegistry()

        file_artifact = registry.register_file(
            artifact_id="art-001",
            run_id="run-123",
            name="build-log",
            path="/tmp/build.log",
            checksum="abc123",
        )
        link_artifact = registry.register_link(
            artifact_id="art-002",
            run_id="run-123",
            name="ci-report",
            url="https://example.com/ci-report",
        )

        artifacts = registry.get_artifacts_for_run("run-123")

        assert file_artifact.type == ArtifactType.FILE
        assert link_artifact.type == ArtifactType.LINK
        assert len(artifacts) == 2
        assert artifacts[0].checksum == "abc123"

    def test_duplicate_artifact_id_rejected(self):
        registry = EvidenceRegistry()
        registry.register_file(
            artifact_id="dup-art",
            run_id="run-123",
            name="log",
            from packages.core.schemas.evidence import (
                CIEvidence,
                EvidenceChain,
                EvidenceType,
                PREvidence,
            )


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
