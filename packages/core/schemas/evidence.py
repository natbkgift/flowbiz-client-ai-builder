"""Evidence and artifact registry schemas."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from packages.core.schemas.gates import GateStatus, GateType


class ArtifactKind(str, Enum):
    """Types of artifacts that can be attached as evidence."""

    FILE = "file"
    LINK = "link"
    LOG = "log"
    METRIC = "metric"


class Artifact(BaseModel):
    """A single artifact stored in the registry."""

    artifact_id: str
    run_id: str
    name: str
    kind: ArtifactKind
    location: str = Field(..., description="Path or URL to the artifact")
    checksum: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_remote(self) -> bool:
        """Return True when the artifact location is a remote URL."""
        return self.location.startswith("http")


class EvidenceType(str, Enum):
    """Categories of evidence captured during a run."""

    PR = "pr"
    CI = "ci"
    DEPLOYMENT = "deployment"
    VERIFICATION = "verification"


class EvidenceRecord(BaseModel):
    """Evidence collected for a specific run and gate."""

    evidence_id: str
    run_id: str
    evidence_type: EvidenceType
    description: str
    gate: Optional[GateType] = None
    status: GateStatus = GateStatus.PENDING
    artifacts: List[Artifact] = Field(default_factory=list)
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def add_artifact(self, artifact: Artifact) -> None:
        """Attach an artifact to this evidence, enforcing run alignment."""
        if artifact.run_id != self.run_id:
            raise ValueError("Artifact run_id must match evidence run_id")
        self.artifacts.append(artifact)

    def mark_passed(self) -> None:
        """Mark evidence as passed."""
        self.status = GateStatus.PASSED

    def mark_failed(self) -> None:
        """Mark evidence as failed."""
        self.status = GateStatus.FAILED

    @property
    def has_artifacts(self) -> bool:
        """Return True when at least one artifact is attached."""
        return len(self.artifacts) > 0


class ArtifactRegistry(BaseModel):
    """Registry that stores artifacts for a run."""

    registry_id: str
    run_id: str
    artifacts: List[Artifact] = Field(default_factory=list)

    def register(self, artifact: Artifact) -> Artifact:
        """Register an artifact, enforcing run alignment."""
        if artifact.run_id != self.run_id:
            raise ValueError("Artifact run_id must match registry run_id")
        self.artifacts.append(artifact)
        return artifact

    def find_by_kind(self, kind: ArtifactKind) -> List[Artifact]:
        """Return all artifacts of the given kind."""
        return [artifact for artifact in self.artifacts if artifact.kind == kind]

    def get(self, artifact_id: str) -> Optional[Artifact]:
        """Retrieve an artifact by id."""
        for artifact in self.artifacts:
            if artifact.artifact_id == artifact_id:
                return artifact
        return None
