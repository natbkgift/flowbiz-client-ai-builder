"""Evidence model definitions for decision audit trails.

This module implements PR #15 — Evidence Model + Artifact Registry v1.
Every decision in the system must have traceable evidence.

BLUEPRINT_REF: PR #15 — Evidence Model + Artifact Registry v1
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    """Types of evidence that can be collected."""

    PR_CREATED = "pr_created"
    PR_UPDATED = "pr_updated"
    PR_MERGED = "pr_merged"
    PR_CLOSED = "pr_closed"
    CI_STARTED = "ci_started"
    CI_PASSED = "ci_passed"
    CI_FAILED = "ci_failed"
    DEPLOY_STARTED = "deploy_started"
    DEPLOY_COMPLETED = "deploy_completed"
    DEPLOY_FAILED = "deploy_failed"
    VERIFY_STARTED = "verify_started"
    VERIFY_PASSED = "verify_passed"
    VERIFY_FAILED = "verify_failed"
    ROLLBACK_TRIGGERED = "rollback_triggered"
    ROLLBACK_COMPLETED = "rollback_completed"
    GATE_PASSED = "gate_passed"
    GATE_FAILED = "gate_failed"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"
    HOTFIX_TRIGGERED = "hotfix_triggered"
    KNOWLEDGE_CREATED = "knowledge_created"


class EvidenceSource(str, Enum):
    """Sources from which evidence can be collected."""

    GITHUB_API = "github_api"
    GITHUB_WEBHOOK = "github_webhook"
    CI_WORKFLOW = "ci_workflow"
    DEPLOY_SCRIPT = "deploy_script"
    AGENT_ACTION = "agent_action"
    MANUAL_INPUT = "manual_input"
    SYSTEM_AUTO = "system_auto"


class Evidence(BaseModel):
    """A single piece of evidence recording an action or decision.

    Evidence is immutable once created - it represents a historical fact
    about what happened in the system.
    """

    evidence_id: str = Field(..., description="Unique identifier for this evidence")
    run_id: str = Field(..., description="ID of the run this evidence belongs to")
    evidence_type: EvidenceType = Field(..., description="Type of evidence")
    source: EvidenceSource = Field(..., description="Source that produced this evidence")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this evidence was recorded",
    )
    actor: str = Field(..., description="Who/what performed the action (user, bot, system)")
    summary: str = Field(..., description="Human-readable summary of what happened")
    details: dict = Field(
        default_factory=dict, description="Structured details about the evidence"
    )
    links: list[str] = Field(
        default_factory=list, description="URLs to related resources (PRs, workflows, etc.)"
    )
    pr_number: Optional[int] = Field(default=None, description="Related PR number if applicable")
    commit_sha: Optional[str] = Field(
        default=None, description="Related commit SHA if applicable"
    )
    environment: Optional[str] = Field(
        default=None, description="Environment (staging/production) if applicable"
    )
    parent_evidence_id: Optional[str] = Field(
        default=None, description="ID of parent evidence if this is a follow-up"
    )


class PREvidence(Evidence):
    """Evidence specifically for PR-related actions."""

    pr_number: int = Field(..., description="PR number this evidence is about")
    pr_title: Optional[str] = Field(default=None, description="Title of the PR")
    pr_url: Optional[str] = Field(default=None, description="URL to the PR")
    base_branch: Optional[str] = Field(default=None, description="Base branch of the PR")
    head_branch: Optional[str] = Field(default=None, description="Head branch of the PR")
    files_changed: int = Field(default=0, description="Number of files changed")
    additions: int = Field(default=0, description="Lines added")
    deletions: int = Field(default=0, description="Lines deleted")


class CIEvidence(Evidence):
    """Evidence specifically for CI pipeline actions."""

    workflow_name: str = Field(..., description="Name of the CI workflow")
    workflow_run_id: Optional[str] = Field(default=None, description="Workflow run ID")
    workflow_url: Optional[str] = Field(default=None, description="URL to the workflow run")
    jobs_passed: int = Field(default=0, description="Number of jobs that passed")
    jobs_failed: int = Field(default=0, description="Number of jobs that failed")
    jobs_skipped: int = Field(default=0, description="Number of jobs that were skipped")
    duration_seconds: Optional[int] = Field(
        default=None, description="Total duration of the CI run in seconds"
    )
    failure_reason: Optional[str] = Field(
        default=None, description="Reason for failure if CI failed"
    )


class DeployEvidence(Evidence):
    """Evidence specifically for deployment actions."""

    environment: str = Field(..., description="Target environment (staging/production)")
    deploy_sha: str = Field(..., description="SHA being deployed")
    deploy_version: Optional[str] = Field(default=None, description="Version being deployed")
    previous_sha: Optional[str] = Field(
        default=None, description="Previous SHA before deployment"
    )
    previous_version: Optional[str] = Field(
        default=None, description="Previous version before deployment"
    )
    deploy_duration_seconds: Optional[int] = Field(
        default=None, description="Duration of deployment in seconds"
    )
    health_check_passed: Optional[bool] = Field(
        default=None, description="Whether health check passed after deploy"
    )
    rollback_triggered: bool = Field(
        default=False, description="Whether rollback was triggered"
    )


class VerifyEvidence(Evidence):
    """Evidence specifically for verification actions."""

    environment: str = Field(..., description="Environment being verified")
    verification_type: str = Field(
        ..., description="Type of verification (smoke, health, functional)"
    )
    checks_passed: int = Field(default=0, description="Number of checks that passed")
    checks_failed: int = Field(default=0, description="Number of checks that failed")
    verification_duration_seconds: Optional[int] = Field(
        default=None, description="Duration of verification in seconds"
    )
    failure_details: Optional[str] = Field(
        default=None, description="Details about failures if any"
    )


class GateEvidence(Evidence):
    """Evidence specifically for gate passage/failure."""

    gate_type: str = Field(
        ..., description="Type of gate (safety, planning, ci, staging, production, learning)"
    )
    gate_result: str = Field(..., description="Result of gate evaluation (passed/failed/skipped)")
    blocking_reason: Optional[str] = Field(
        default=None, description="Reason for blocking if gate failed"
    )
    requirements_met: list[str] = Field(
        default_factory=list, description="Requirements that were met"
    )
    requirements_missing: list[str] = Field(
        default_factory=list, description="Requirements that were missing"
    )


class EvidenceChain(BaseModel):
    """A chain of related evidence for a single run.

    Provides a complete audit trail of what happened during a run,
    enabling anyone to understand "what was done" by reviewing the chain.
    """

    chain_id: str = Field(..., description="Unique identifier for this chain")
    run_id: str = Field(..., description="ID of the run this chain belongs to")
    pr_number: Optional[int] = Field(default=None, description="Related PR number")
    feature_name: Optional[str] = Field(default=None, description="Feature being delivered")
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this run started",
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="When this run completed"
    )
    evidence_items: list[Evidence] = Field(
        default_factory=list, description="All evidence items in this chain"
    )
    current_status: str = Field(
        default="in_progress", description="Current status of the run"
    )

    def add_evidence(self, evidence: Evidence) -> None:
        """Add a new piece of evidence to the chain.

        Args:
            evidence: The evidence to add
        """
        self.evidence_items.append(evidence)

    def get_evidence_by_type(self, evidence_type: EvidenceType) -> list[Evidence]:
        """Get all evidence of a specific type.

        Args:
            evidence_type: The type of evidence to filter by

        Returns:
            List of evidence items matching the type
        """
        return [e for e in self.evidence_items if e.evidence_type == evidence_type]

    def get_latest_evidence(self) -> Optional[Evidence]:
        """Get the most recent evidence item.

        Returns:
            The most recent evidence item, or None if chain is empty
        """
        if not self.evidence_items:
            return None
        return max(self.evidence_items, key=lambda e: e.timestamp)

    def get_evidence_summary(self) -> dict:
        """Get a summary of evidence in the chain.

        Returns:
            Dictionary with counts of evidence by type and status information
        """
        summary: dict = {
            "total_evidence_count": len(self.evidence_items),
            "evidence_by_type": {},
            "has_failures": False,
            "latest_action": None,
        }

        for evidence in self.evidence_items:
            type_name = evidence.evidence_type.value
            summary["evidence_by_type"][type_name] = (
                summary["evidence_by_type"].get(type_name, 0) + 1
            )
            if "failed" in type_name or "denied" in type_name:
                summary["has_failures"] = True

        latest = self.get_latest_evidence()
        if latest:
            summary["latest_action"] = {
                "type": latest.evidence_type.value,
                "summary": latest.summary,
                "timestamp": latest.timestamp.isoformat(),
            }

        return summary

    def is_complete(self) -> bool:
        """Check if the evidence chain represents a completed run.

        Returns:
            True if the run has completed (merged, closed, or failed terminally)
        """
        terminal_types = {
            EvidenceType.PR_MERGED,
            EvidenceType.PR_CLOSED,
            EvidenceType.ROLLBACK_COMPLETED,
        }
        return any(e.evidence_type in terminal_types for e in self.evidence_items)

    def mark_complete(self, status: str = "completed") -> None:
        """Mark the evidence chain as complete.

        Args:
            status: Final status of the run
        """
        self.completed_at = datetime.now(timezone.utc)
        self.current_status = status
