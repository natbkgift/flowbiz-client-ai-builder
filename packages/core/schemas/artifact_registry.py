"""Artifact registry for run-linked evidence.

Blueprint PR #15: Evidence Model + Artifact Registry v1

This module provides a lightweight, in-memory registry for artifacts that can be
referenced by evidence items. Artifacts are file/link based to keep the system
storage-agnostic.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ArtifactType(str, Enum):
    """Supported artifact reference types."""

    FILE = "file"
    LINK = "link"


class ArtifactReference(BaseModel):
    """A reference to an artifact related to a run."""

    artifact_id: str
    run_id: str
    artifact_type: ArtifactType
    uri: str = Field(
        ..., description="Path or URL to the artifact (storage-agnostic reference)"
    )
    label: Optional[str] = Field(default=None, description="Short human label")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArtifactRegistry(BaseModel):
    """In-memory artifact registry with run-based indexing."""

    artifacts: dict[str, ArtifactReference] = Field(default_factory=dict)

    def add(self, artifact: ArtifactReference) -> None:
        if artifact.artifact_id in self.artifacts:
            raise ValueError(f"artifact_id already exists: {artifact.artifact_id}")
        self.artifacts[artifact.artifact_id] = artifact

    def get(self, artifact_id: str) -> ArtifactReference:
        if artifact_id not in self.artifacts:
            raise KeyError(f"artifact_id not found: {artifact_id}")
        return self.artifacts[artifact_id]

    def list_by_run(self, run_id: str) -> list[ArtifactReference]:
        return [a for a in self.artifacts.values() if a.run_id == run_id]

    def get_run_summary(self, run_id: str) -> dict[str, Any]:
        artifacts = self.list_by_run(run_id)
        counts = Counter(a.artifact_type.value for a in artifacts)

        return {
            "run_id": run_id,
            "total": len(artifacts),
            "by_type": counts,
            "artifact_ids": [a.artifact_id for a in artifacts],
        }


def create_file_artifact(
    *, run_id: str, artifact_id: str, path: str, label: Optional[str] = None
) -> ArtifactReference:
    return ArtifactReference(
        artifact_id=artifact_id,
        run_id=run_id,
        artifact_type=ArtifactType.FILE,
        uri=path,
        label=label,
    )


def create_link_artifact(
    *, run_id: str, artifact_id: str, url: str, label: Optional[str] = None
) -> ArtifactReference:
    return ArtifactReference(
        artifact_id=artifact_id,
        run_id=run_id,
        artifact_type=ArtifactType.LINK,
        uri=url,
        label=label,
    )
