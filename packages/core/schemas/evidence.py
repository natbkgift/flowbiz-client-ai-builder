"""Evidence and artifact registry models."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    """Supported evidence categories for a run."""

    PR = "pr"
    CI = "ci"
    DEPLOY = "deploy"
    VERIFY = "verify"


class EvidenceStatus(str, Enum):
    """Status of a captured evidence item."""

    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


class ArtifactType(str, Enum):
    """Types of artifacts that can be registered."""

    FILE = "file"
    LINK = "link"


class ArtifactRecord(BaseModel):
    """Record describing a file or link artifact tied to a run."""

    artifact_id: str
    run_id: str
    name: str
    type: ArtifactType
    location: str
    description: Optional[str] = None
    checksum: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvidenceRecord(BaseModel):
    """Evidence entry describing what happened in a run step."""

    evidence_id: str
    run_id: str
    type: EvidenceType
    title: str
    description: str
    status: EvidenceStatus = EvidenceStatus.PENDING
    artifact_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def attach_artifact(self, artifact: ArtifactRecord) -> None:
        """Attach an artifact to this evidence."""
        if artifact.run_id != self.run_id:
            raise ValueError("Artifact run_id must match evidence run_id")

        if artifact.artifact_id not in self.artifact_ids:
            self.artifact_ids.append(artifact.artifact_id)


class EvidenceRegistry(BaseModel):
    """In-memory registry for evidence and artifacts per run."""

    evidences: List[EvidenceRecord] = Field(default_factory=list)
    artifacts: List[ArtifactRecord] = Field(default_factory=list)
    evidence_index: Dict[str, EvidenceRecord] = Field(default_factory=dict)
    artifact_index: Dict[str, ArtifactRecord] = Field(default_factory=dict)

    def register_file(
        self,
        *,
        artifact_id: str,
        run_id: str,
        name: str,
        path: str,
        description: Optional[str] = None,
        checksum: Optional[str] = None,
    ) -> ArtifactRecord:
        """Register a file artifact."""
        if artifact_id in self.artifact_index:
            raise ValueError(f"Artifact already exists: {artifact_id}")

        record = ArtifactRecord(
            artifact_id=artifact_id,
            run_id=run_id,
            name=name,
            type=ArtifactType.FILE,
            location=path,
            description=description,
            checksum=checksum,
        )
        self.artifacts.append(record)
        self.artifact_index[record.artifact_id] = record
        return record

    def register_link(
        self,
        *,
        artifact_id: str,
        run_id: str,
        name: str,
        url: str,
        description: Optional[str] = None,
    ) -> ArtifactRecord:
        """Register a link-based artifact."""
        if artifact_id in self.artifact_index:
            raise ValueError(f"Artifact already exists: {artifact_id}")

        record = ArtifactRecord(
            artifact_id=artifact_id,
            run_id=run_id,
            name=name,
            type=ArtifactType.LINK,
            location=url,
            description=description,
        )
        self.artifacts.append(record)
        self.artifact_index[record.artifact_id] = record
        return record

    def add_evidence_entry(
        self,
        *,
        evidence_id: str,
        run_id: str,
        evidence_type: EvidenceType,
        title: str,
        description: str,
        status: EvidenceStatus = EvidenceStatus.PENDING,
        artifact_ids: Optional[List[str]] = None,
    ) -> EvidenceRecord:
        """Add a new evidence entry for a run."""
        if evidence_id in self.evidence_index:
            raise ValueError(f"Evidence already exists: {evidence_id}")

        entry = EvidenceRecord(
            evidence_id=evidence_id,
            run_id=run_id,
            type=evidence_type,
            title=title,
            description=description,
            status=status,
            artifact_ids=artifact_ids or [],
        )
        self.evidences.append(entry)
        self.evidence_index[entry.evidence_id] = entry
        return entry

    def attach_artifact_to_evidence(self, *, evidence_id: str, artifact_id: str) -> EvidenceRecord:
        """Attach an artifact to a specific evidence entry."""
        evidence = self._get_evidence_by_id(evidence_id)
        artifact = self._get_artifact_by_id(artifact_id)

        evidence.attach_artifact(artifact)
        return evidence

    def get_run_evidence(self, run_id: str) -> List[EvidenceRecord]:
        """Return evidence entries for a run."""
        return [entry for entry in self.evidence_index.values() if entry.run_id == run_id]

    def get_artifacts_for_run(self, run_id: str) -> List[ArtifactRecord]:
        """Return artifact entries for a run."""
        return [artifact for artifact in self.artifact_index.values() if artifact.run_id == run_id]

    def is_run_fully_documented(self, run_id: str) -> bool:
        """Check that all required evidence types are present and not failed."""
        entries = self.get_run_evidence(run_id)
        for evidence_type in EvidenceType:
            type_entries = [entry for entry in entries if entry.type == evidence_type]
            if not type_entries:
                return False

            latest_entry = max(type_entries, key=lambda entry: entry.created_at)
            if latest_entry.status == EvidenceStatus.FAILED:
                return False

        return True

    def build_run_timeline(self, run_id: str) -> List[Dict[str, Any]]:
        """Build a chronological view of evidence and artifacts for a run."""
        events = [
            {
                "event": "evidence",
                "id": entry.evidence_id,
                "type": entry.type.value,
                "status": entry.status.value,
                "created_at": entry.created_at.isoformat(),
            }
            for entry in self.get_run_evidence(run_id)
        ]

        events.extend(
            {
                "event": "artifact",
                "id": artifact.artifact_id,
                "type": artifact.type.value,
                "location": artifact.location,
                "created_at": artifact.created_at.isoformat(),
            }
            for artifact in self.get_artifacts_for_run(run_id)
        )

        return sorted(events, key=lambda event: event["created_at"])

    def _get_evidence_by_id(self, evidence_id: str) -> EvidenceRecord:
        try:
            return self.evidence_index[evidence_id]
        except KeyError as exc:
            raise ValueError(f"Evidence not found: {evidence_id}") from exc

    def _get_artifact_by_id(self, artifact_id: str) -> ArtifactRecord:
        try:
            return self.artifact_index[artifact_id]
        except KeyError as exc:
            raise ValueError(f"Artifact not found: {artifact_id}") from exc
