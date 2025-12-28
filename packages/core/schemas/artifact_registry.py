"""Artifact Registry for managing evidence and knowledge artifacts.

This module implements PR #15 — Evidence Model + Artifact Registry v1.
Provides a registry for storing, retrieving, and linking artifacts to runs.

BLUEPRINT_REF: PR #15 — Evidence Model + Artifact Registry v1
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ArtifactType(str, Enum):
    """Types of artifacts that can be stored in the registry."""

    # Evidence artifacts
    EVIDENCE_CHAIN = "evidence_chain"
    PR_EVIDENCE = "pr_evidence"
    CI_EVIDENCE = "ci_evidence"
    DEPLOY_EVIDENCE = "deploy_evidence"
    VERIFY_EVIDENCE = "verify_evidence"
    GATE_EVIDENCE = "gate_evidence"

    # Knowledge artifacts
    FEATURE_SUMMARY = "feature_summary"
    LESSONS_LEARNED = "lessons_learned"
    TEST_GAPS = "test_gaps"
    DEPLOY_NOTES = "deploy_notes"
    KNOWLEDGE_BUNDLE = "knowledge_bundle"

    # Other artifacts
    LOG_FILE = "log_file"
    SCREENSHOT = "screenshot"
    REPORT = "report"
    CONFIG_SNAPSHOT = "config_snapshot"


class ArtifactStorageType(str, Enum):
    """Storage backends for artifacts."""

    FILE_LOCAL = "file_local"
    FILE_REMOTE = "file_remote"
    INLINE_JSON = "inline_json"
    EXTERNAL_LINK = "external_link"
    GITHUB_ARTIFACT = "github_artifact"


class ArtifactMetadata(BaseModel):
    """Metadata about an artifact in the registry."""

    artifact_id: str = Field(..., description="Unique identifier for this artifact")
    artifact_type: ArtifactType = Field(..., description="Type of artifact")
    storage_type: ArtifactStorageType = Field(
        ..., description="How the artifact is stored"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this artifact was created",
    )
    created_by: str = Field(..., description="Who/what created this artifact")
    run_id: str = Field(..., description="ID of the run this artifact belongs to")
    pr_number: Optional[int] = Field(default=None, description="Related PR number")
    name: str = Field(..., description="Human-readable name for the artifact")
    description: Optional[str] = Field(
        default=None, description="Description of the artifact"
    )
    size_bytes: Optional[int] = Field(
        default=None, description="Size of the artifact in bytes"
    )
    content_type: str = Field(
        default="application/json", description="MIME type of the artifact content"
    )
    checksum: Optional[str] = Field(
        default=None, description="SHA256 checksum of the artifact content"
    )
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    retention_days: Optional[int] = Field(
        default=None, description="How many days to retain this artifact"
    )


class ArtifactReference(BaseModel):
    """A reference to an artifact's storage location."""

    artifact_id: str = Field(..., description="ID of the artifact being referenced")
    storage_type: ArtifactStorageType = Field(..., description="Storage type")
    location: str = Field(
        ..., description="Location of the artifact (path, URL, or inline content)"
    )
    inline_content: Optional[dict] = Field(
        default=None, description="Inline JSON content if storage_type is INLINE_JSON"
    )


class ArtifactRegistryEntry(BaseModel):
    """A complete entry in the artifact registry."""

    metadata: ArtifactMetadata
    reference: ArtifactReference

    def get_artifact_path(self) -> str:
        """Get the path or URL to access this artifact.

        Returns:
            Path or URL string
        """
        if self.reference.storage_type == ArtifactStorageType.INLINE_JSON:
            return f"inline://{self.metadata.artifact_id}"
        return self.reference.location

    def is_accessible(self) -> bool:
        """Check if the artifact is accessible (basic validation).

        Returns:
            True if artifact appears accessible
        """
        if self.reference.storage_type == ArtifactStorageType.INLINE_JSON:
            return self.reference.inline_content is not None
        return bool(self.reference.location)


class ArtifactRegistry(BaseModel):
    """Registry for managing all artifacts associated with runs.

    Provides indexing by run_id, PR number, and artifact type for
    efficient retrieval and audit trail construction.
    """

    registry_id: str = Field(..., description="Unique identifier for this registry")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this registry was created",
    )
    entries: list[ArtifactRegistryEntry] = Field(
        default_factory=list, description="All artifact entries in this registry"
    )
    # Indexes for efficient lookup
    _by_run_id: dict[str, list[str]] = Field(default_factory=dict)
    _by_pr_number: dict[int, list[str]] = Field(default_factory=dict)
    _by_type: dict[str, list[str]] = Field(default_factory=dict)

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True

    def __init__(self, **data):
        """Initialize registry and rebuild indexes."""
        super().__init__(**data)
        self._rebuild_indexes()

    def _rebuild_indexes(self) -> None:
        """Rebuild all lookup indexes from entries."""
        self._by_run_id = {}
        self._by_pr_number = {}
        self._by_type = {}

        for entry in self.entries:
            artifact_id = entry.metadata.artifact_id
            run_id = entry.metadata.run_id

            # Index by run_id
            if run_id not in self._by_run_id:
                self._by_run_id[run_id] = []
            self._by_run_id[run_id].append(artifact_id)

            # Index by PR number
            if entry.metadata.pr_number is not None:
                pr_num = entry.metadata.pr_number
                if pr_num not in self._by_pr_number:
                    self._by_pr_number[pr_num] = []
                self._by_pr_number[pr_num].append(artifact_id)

            # Index by type
            type_name = entry.metadata.artifact_type.value
            if type_name not in self._by_type:
                self._by_type[type_name] = []
            self._by_type[type_name].append(artifact_id)

    def register_artifact(self, entry: ArtifactRegistryEntry) -> str:
        """Register a new artifact in the registry.

        Args:
            entry: The artifact entry to register

        Returns:
            The artifact_id of the registered artifact
        """
        self.entries.append(entry)
        artifact_id = entry.metadata.artifact_id
        run_id = entry.metadata.run_id

        # Update indexes
        if run_id not in self._by_run_id:
            self._by_run_id[run_id] = []
        self._by_run_id[run_id].append(artifact_id)

        if entry.metadata.pr_number is not None:
            pr_num = entry.metadata.pr_number
            if pr_num not in self._by_pr_number:
                self._by_pr_number[pr_num] = []
            self._by_pr_number[pr_num].append(artifact_id)

        type_name = entry.metadata.artifact_type.value
        if type_name not in self._by_type:
            self._by_type[type_name] = []
        self._by_type[type_name].append(artifact_id)

        return artifact_id

    def get_artifact(self, artifact_id: str) -> Optional[ArtifactRegistryEntry]:
        """Get a specific artifact by ID.

        Args:
            artifact_id: The ID of the artifact to retrieve

        Returns:
            The artifact entry, or None if not found
        """
        for entry in self.entries:
            if entry.metadata.artifact_id == artifact_id:
                return entry
        return None

    def get_artifacts_by_run(self, run_id: str) -> list[ArtifactRegistryEntry]:
        """Get all artifacts for a specific run.

        Args:
            run_id: The run ID to filter by

        Returns:
            List of artifact entries for the run
        """
        artifact_ids = self._by_run_id.get(run_id, [])
        return [
            entry
            for entry in self.entries
            if entry.metadata.artifact_id in artifact_ids
        ]

    def get_artifacts_by_pr(self, pr_number: int) -> list[ArtifactRegistryEntry]:
        """Get all artifacts for a specific PR.

        Args:
            pr_number: The PR number to filter by

        Returns:
            List of artifact entries for the PR
        """
        artifact_ids = self._by_pr_number.get(pr_number, [])
        return [
            entry
            for entry in self.entries
            if entry.metadata.artifact_id in artifact_ids
        ]

    def get_artifacts_by_type(
        self, artifact_type: ArtifactType
    ) -> list[ArtifactRegistryEntry]:
        """Get all artifacts of a specific type.

        Args:
            artifact_type: The type of artifacts to retrieve

        Returns:
            List of artifact entries of the specified type
        """
        artifact_ids = self._by_type.get(artifact_type.value, [])
        return [
            entry
            for entry in self.entries
            if entry.metadata.artifact_id in artifact_ids
        ]

    def get_run_summary(self, run_id: str) -> dict:
        """Get a summary of all artifacts for a run.

        This enables viewing a run and understanding "what was done"
        per BLUEPRINT requirement.

        Args:
            run_id: The run ID to summarize

        Returns:
            Dictionary with artifact counts and details by type
        """
        artifacts = self.get_artifacts_by_run(run_id)
        summary: dict = {
            "run_id": run_id,
            "total_artifacts": len(artifacts),
            "artifacts_by_type": {},
            "artifact_list": [],
        }

        for entry in artifacts:
            type_name = entry.metadata.artifact_type.value
            summary["artifacts_by_type"][type_name] = (
                summary["artifacts_by_type"].get(type_name, 0) + 1
            )
            summary["artifact_list"].append(
                {
                    "id": entry.metadata.artifact_id,
                    "name": entry.metadata.name,
                    "type": type_name,
                    "created_at": entry.metadata.created_at.isoformat(),
                    "location": entry.get_artifact_path(),
                }
            )

        return summary

    def delete_artifact(self, artifact_id: str) -> bool:
        """Delete an artifact from the registry.

        Args:
            artifact_id: The ID of the artifact to delete

        Returns:
            True if deleted, False if not found
        """
        for i, entry in enumerate(self.entries):
            if entry.metadata.artifact_id == artifact_id:
                self.entries.pop(i)
                self._rebuild_indexes()
                return True
        return False

    def get_artifact_count(self) -> int:
        """Get the total number of artifacts in the registry.

        Returns:
            Total artifact count
        """
        return len(self.entries)


def create_evidence_artifact(
    evidence_data: dict,
    run_id: str,
    artifact_id: str,
    created_by: str,
    pr_number: Optional[int] = None,
    artifact_type: ArtifactType = ArtifactType.EVIDENCE_CHAIN,
) -> ArtifactRegistryEntry:
    """Helper function to create an evidence artifact entry.

    Args:
        evidence_data: The evidence data to store
        run_id: ID of the run
        artifact_id: Unique ID for this artifact
        created_by: Who created this artifact
        pr_number: Optional PR number
        artifact_type: Type of evidence artifact

    Returns:
        A complete artifact registry entry
    """
    metadata = ArtifactMetadata(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        storage_type=ArtifactStorageType.INLINE_JSON,
        created_by=created_by,
        run_id=run_id,
        pr_number=pr_number,
        name=f"Evidence: {artifact_type.value}",
        description=f"Evidence artifact for run {run_id}",
        content_type="application/json",
        tags=["evidence", artifact_type.value],
    )

    reference = ArtifactReference(
        artifact_id=artifact_id,
        storage_type=ArtifactStorageType.INLINE_JSON,
        location=f"inline://{artifact_id}",
        inline_content=evidence_data,
    )

    return ArtifactRegistryEntry(metadata=metadata, reference=reference)


def create_knowledge_artifact(
    knowledge_data: dict,
    run_id: str,
    artifact_id: str,
    created_by: str,
    pr_number: Optional[int] = None,
    artifact_type: ArtifactType = ArtifactType.KNOWLEDGE_BUNDLE,
    name: Optional[str] = None,
) -> ArtifactRegistryEntry:
    """Helper function to create a knowledge artifact entry.

    Args:
        knowledge_data: The knowledge data to store
        run_id: ID of the run
        artifact_id: Unique ID for this artifact
        created_by: Who created this artifact
        pr_number: Optional PR number
        artifact_type: Type of knowledge artifact
        name: Optional custom name for the artifact

    Returns:
        A complete artifact registry entry
    """
    metadata = ArtifactMetadata(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        storage_type=ArtifactStorageType.INLINE_JSON,
        created_by=created_by,
        run_id=run_id,
        pr_number=pr_number,
        name=name or f"Knowledge: {artifact_type.value}",
        description=f"Knowledge artifact for run {run_id}",
        content_type="application/json",
        tags=["knowledge", artifact_type.value],
    )

    reference = ArtifactReference(
        artifact_id=artifact_id,
        storage_type=ArtifactStorageType.INLINE_JSON,
        location=f"inline://{artifact_id}",
        inline_content=knowledge_data,
    )

    return ArtifactRegistryEntry(metadata=metadata, reference=reference)


def create_file_artifact(
    file_path: str,
    run_id: str,
    artifact_id: str,
    created_by: str,
    artifact_type: ArtifactType,
    name: str,
    pr_number: Optional[int] = None,
    size_bytes: Optional[int] = None,
    content_type: str = "application/octet-stream",
) -> ArtifactRegistryEntry:
    """Helper function to create a file-based artifact entry.

    Args:
        file_path: Path to the file
        run_id: ID of the run
        artifact_id: Unique ID for this artifact
        created_by: Who created this artifact
        artifact_type: Type of artifact
        name: Human-readable name
        pr_number: Optional PR number
        size_bytes: Optional file size
        content_type: MIME type of the file

    Returns:
        A complete artifact registry entry
    """
    metadata = ArtifactMetadata(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        storage_type=ArtifactStorageType.FILE_LOCAL,
        created_by=created_by,
        run_id=run_id,
        pr_number=pr_number,
        name=name,
        description=f"File artifact: {file_path}",
        size_bytes=size_bytes,
        content_type=content_type,
        tags=["file", artifact_type.value],
    )

    reference = ArtifactReference(
        artifact_id=artifact_id,
        storage_type=ArtifactStorageType.FILE_LOCAL,
        location=file_path,
    )

    return ArtifactRegistryEntry(metadata=metadata, reference=reference)


def create_link_artifact(
    url: str,
    run_id: str,
    artifact_id: str,
    created_by: str,
    artifact_type: ArtifactType,
    name: str,
    pr_number: Optional[int] = None,
    description: Optional[str] = None,
) -> ArtifactRegistryEntry:
    """Helper function to create a link-based artifact entry.

    Args:
        url: External URL to the artifact
        run_id: ID of the run
        artifact_id: Unique ID for this artifact
        created_by: Who created this artifact
        artifact_type: Type of artifact
        name: Human-readable name
        pr_number: Optional PR number
        description: Optional description

    Returns:
        A complete artifact registry entry
    """
    metadata = ArtifactMetadata(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        storage_type=ArtifactStorageType.EXTERNAL_LINK,
        created_by=created_by,
        run_id=run_id,
        pr_number=pr_number,
        name=name,
        description=description or f"External link: {url}",
        content_type="text/uri-list",
        tags=["link", artifact_type.value],
    )

    reference = ArtifactReference(
        artifact_id=artifact_id,
        storage_type=ArtifactStorageType.EXTERNAL_LINK,
        location=url,
    )

    return ArtifactRegistryEntry(metadata=metadata, reference=reference)
