"""Tests for evidence and artifact registry."""

from datetime import datetime, timedelta, timezone

import pytest

from packages.core.schemas.evidence import (
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


class TestEvidenceRegistration:
    """Tests for evidence registration and attachment."""

    def test_add_evidence_and_attach_artifact(self):
        registry = EvidenceRegistry()
        artifact = registry.register_file(
            artifact_id="artifact-1",
            run_id="run-123",
            name="deploy-log",
            path="/tmp/deploy.log",
        )

        evidence = registry.add_evidence_entry(
            evidence_id="evidence-1",
            run_id="run-123",
            evidence_type=EvidenceType.DEPLOY,
            title="Deployment",
            description="Deployment to staging passed",
            status=EvidenceStatus.PASSED,
        )

        updated = registry.attach_artifact_to_evidence(
            evidence_id=evidence.evidence_id,
            artifact_id=artifact.artifact_id,
        )

        assert updated.artifact_ids == [artifact.artifact_id]

    def test_attach_artifact_requires_matching_run(self):
        registry = EvidenceRegistry()
        artifact = registry.register_file(
            artifact_id="artifact-2",
            run_id="run-A",
            name="log",
            path="/tmp/log.txt",
        )

        evidence = registry.add_evidence_entry(
            evidence_id="evidence-2",
            run_id="run-B",
            evidence_type=EvidenceType.CI,
            title="CI",
            description="CI run for different run id",
        )

        with pytest.raises(ValueError, match="run_id"):
            evidence.attach_artifact(artifact)


class TestRunDocumentation:
    """Tests for run documentation completeness and timeline."""

    def test_is_run_fully_documented(self):
        registry = EvidenceRegistry()
        for evidence_type in EvidenceType:
            registry.add_evidence_entry(
                evidence_id=f"ev-{evidence_type.value}",
                run_id="run-123",
                evidence_type=evidence_type,
                title=evidence_type.value,
                description=f"{evidence_type.value} evidence",
                status=EvidenceStatus.PASSED,
            )

        assert registry.is_run_fully_documented("run-123") is True

        registry.add_evidence_entry(
            evidence_id="ev-pr-failed",
            run_id="run-123",
            evidence_type=EvidenceType.PR,
            title="PR failed",
            description="Rejected by policy",
            status=EvidenceStatus.FAILED,
        )

        assert registry.is_run_fully_documented("run-123") is False

    def test_build_run_timeline(self):
        registry = EvidenceRegistry()
        base_time = datetime.now(timezone.utc)

        ev_pr = registry.add_evidence_entry(
            evidence_id="ev-pr",
            run_id="run-321",
            evidence_type=EvidenceType.PR,
            title="PR opened",
            description="PR created",
        )
        ev_pr.created_at = base_time

        artifact = registry.register_link(
            artifact_id="art-1",
            run_id="run-321",
            name="check-run",
            url="https://example.com/checks",
        )
        artifact.created_at = base_time + timedelta(minutes=1)

        ev_ci = registry.add_evidence_entry(
            evidence_id="ev-ci",
            run_id="run-321",
            evidence_type=EvidenceType.CI,
            title="CI green",
            description="All checks passed",
        )
        ev_ci.created_at = base_time + timedelta(minutes=2)

        timeline = registry.build_run_timeline("run-321")

        assert [event["id"] for event in timeline] == ["ev-pr", "art-1", "ev-ci"]
        assert timeline[0]["event"] == "evidence"
        assert timeline[1]["event"] == "artifact"
