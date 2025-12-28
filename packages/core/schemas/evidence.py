"""Evidence models linked to a run.

Blueprint PR #15: Evidence Model + Artifact Registry v1

Evidence items record what happened during a run (PR, CI, deploy, verify) and can
optionally reference artifacts stored in an ArtifactRegistry by ID.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    """Core evidence categories required by the Blueprint."""

    PR = "pr"
    CI = "ci"
    DEPLOY = "deploy"
    VERIFY = "verify"


class EvidenceSource(str, Enum):
    """Where the evidence originated from."""

    GITHUB = "github"
    CI_SYSTEM = "ci_system"
    MANUAL = "manual"


class Evidence(BaseModel):
    """Base evidence record."""

    evidence_id: str
    run_id: str
    evidence_type: EvidenceType
    source: EvidenceSource = EvidenceSource.MANUAL
    summary: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    artifact_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def attach_artifact(self, artifact_id: str) -> None:
        if artifact_id not in self.artifact_ids:
            self.artifact_ids.append(artifact_id)


class PREvidence(Evidence):
    evidence_type: EvidenceType = EvidenceType.PR

    pr_number: int
    pr_url: Optional[str] = None
    title: Optional[str] = None


class CIEvidence(Evidence):
    evidence_type: EvidenceType = EvidenceType.CI

    workflow_name: str
    conclusion: Optional[str] = None
    run_url: Optional[str] = None


class DeployEvidence(Evidence):
    evidence_type: EvidenceType = EvidenceType.DEPLOY

    environment: str = Field(..., description="e.g. staging | production")
    sha: Optional[str] = None
    status: Optional[str] = None


class VerifyEvidence(Evidence):
    evidence_type: EvidenceType = EvidenceType.VERIFY

    check_name: str
    passed: bool
    notes: Optional[str] = None


class EvidenceChain(BaseModel):
    """A run-scoped collection of evidence items."""

    run_id: str
    items: list[Evidence] = Field(default_factory=list)

    def add(self, evidence: Evidence) -> None:
        if evidence.run_id != self.run_id:
            raise ValueError(
                f"evidence.run_id ({evidence.run_id}) does not match chain.run_id ({self.run_id})"
            )
        self.items.append(evidence)

    def list_by_type(self, evidence_type: EvidenceType) -> list[Evidence]:
        return [e for e in self.items if e.evidence_type == evidence_type]

    def latest(self) -> Optional[Evidence]:
        if not self.items:
            return None
        return max(self.items, key=lambda e: e.created_at)

    def summary(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for item in self.items:
            key = item.evidence_type.value
            counts[key] = counts.get(key, 0) + 1

        latest = self.latest()
        return {
            "run_id": self.run_id,
            "total": len(self.items),
            "by_type": counts,
            "latest_evidence_id": latest.evidence_id if latest else None,
        }
