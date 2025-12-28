"""Tests for evidence and artifact registry schemas."""

import pytest

from packages.core.schemas.evidence import (
    Artifact,
    ArtifactKind,
    ArtifactRegistry,
    EvidenceRecord,
    EvidenceType,
)
from packages.core.schemas.gates import GateStatus, GateType


def test_artifact_registry_register_and_find_by_kind():
    """Artifacts are registered and discovered by kind."""
    registry = ArtifactRegistry(registry_id="registry-1", run_id="run-123")
    artifact = Artifact(
        artifact_id="art-1",
        run_id="run-123",
        name="lint-report",
        kind=ArtifactKind.LINK,
        location="https://example.com/lint-report",
    )

    registry.register(artifact)

    link_artifacts = registry.find_by_kind(ArtifactKind.LINK)
    assert registry.get("art-1") == artifact
    assert link_artifacts == [artifact]
    assert artifact.is_remote is True


def test_artifact_registry_enforces_run_alignment():
    """Run identifiers must match when registering artifacts."""
    registry = ArtifactRegistry(registry_id="registry-1", run_id="run-123")
    artifact = Artifact(
        artifact_id="art-1",
        run_id="other-run",
        name="lint-report",
        kind=ArtifactKind.LINK,
        location="https://example.com/lint-report",
    )

    with pytest.raises(ValueError):
        registry.register(artifact)


def test_evidence_record_status_and_artifacts():
    """Evidence records manage status and attached artifacts."""
    evidence = EvidenceRecord(
        evidence_id="ev-1",
        run_id="run-123",
        evidence_type=EvidenceType.CI,
        description="CI results",
        gate=GateType.CI,
    )
    artifact = Artifact(
        artifact_id="art-1",
        run_id="run-123",
        name="ci-report",
        kind=ArtifactKind.FILE,
        location="/tmp/ci-report.json",
    )

    evidence.add_artifact(artifact)
    evidence.mark_passed()

    assert evidence.status == GateStatus.PASSED
    assert evidence.has_artifacts is True
    assert evidence.artifacts[0].name == "ci-report"


def test_evidence_rejects_mismatched_artifact_run():
    """Evidence rejects artifacts that belong to another run."""
    evidence = EvidenceRecord(
        evidence_id="ev-1",
        run_id="run-123",
        evidence_type=EvidenceType.PR,
        description="PR evidence",
    )
    artifact = Artifact(
        artifact_id="art-1",
        run_id="other-run",
        name="pr-template",
        kind=ArtifactKind.FILE,
        location="/tmp/pr-template.md",
    )

    with pytest.raises(ValueError):
        evidence.add_artifact(artifact)
