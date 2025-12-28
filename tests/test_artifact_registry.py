"""Tests for Artifact Registry.

Tests for PR #15 — Evidence Model + Artifact Registry v1.
BLUEPRINT_REF: PR #15 — Evidence Model + Artifact Registry v1
"""

from packages.core.schemas.artifact_registry import (
    ArtifactMetadata,
    ArtifactReference,
    ArtifactRegistry,
    ArtifactRegistryEntry,
    ArtifactStorageType,
    ArtifactType,
    create_evidence_artifact,
    create_file_artifact,
    create_knowledge_artifact,
    create_link_artifact,
)


class TestArtifactType:
    """Tests for ArtifactType enum."""

    def test_evidence_artifact_types(self):
        """Evidence artifact types should be defined."""
        assert ArtifactType.EVIDENCE_CHAIN == "evidence_chain"
        assert ArtifactType.PR_EVIDENCE == "pr_evidence"
        assert ArtifactType.CI_EVIDENCE == "ci_evidence"
        assert ArtifactType.DEPLOY_EVIDENCE == "deploy_evidence"
        assert ArtifactType.VERIFY_EVIDENCE == "verify_evidence"
        assert ArtifactType.GATE_EVIDENCE == "gate_evidence"

    def test_knowledge_artifact_types(self):
        """Knowledge artifact types should be defined."""
        assert ArtifactType.FEATURE_SUMMARY == "feature_summary"
        assert ArtifactType.LESSONS_LEARNED == "lessons_learned"
        assert ArtifactType.TEST_GAPS == "test_gaps"
        assert ArtifactType.DEPLOY_NOTES == "deploy_notes"
        assert ArtifactType.KNOWLEDGE_BUNDLE == "knowledge_bundle"

    def test_other_artifact_types(self):
        """Other artifact types should be defined."""
        assert ArtifactType.LOG_FILE == "log_file"
        assert ArtifactType.SCREENSHOT == "screenshot"
        assert ArtifactType.REPORT == "report"
        assert ArtifactType.CONFIG_SNAPSHOT == "config_snapshot"


class TestArtifactStorageType:
    """Tests for ArtifactStorageType enum."""

    def test_storage_types(self):
        """All storage types should be defined."""
        assert ArtifactStorageType.FILE_LOCAL == "file_local"
        assert ArtifactStorageType.FILE_REMOTE == "file_remote"
        assert ArtifactStorageType.INLINE_JSON == "inline_json"
        assert ArtifactStorageType.EXTERNAL_LINK == "external_link"
        assert ArtifactStorageType.GITHUB_ARTIFACT == "github_artifact"


class TestArtifactMetadata:
    """Tests for ArtifactMetadata model."""

    def test_create_basic_metadata(self):
        """Should create metadata with required fields."""
        metadata = ArtifactMetadata(
            artifact_id="art-001",
            artifact_type=ArtifactType.EVIDENCE_CHAIN,
            storage_type=ArtifactStorageType.INLINE_JSON,
            created_by="system",
            run_id="run-001",
            name="Evidence Chain",
        )

        assert metadata.artifact_id == "art-001"
        assert metadata.artifact_type == ArtifactType.EVIDENCE_CHAIN
        assert metadata.storage_type == ArtifactStorageType.INLINE_JSON
        assert metadata.created_by == "system"
        assert metadata.run_id == "run-001"
        assert metadata.name == "Evidence Chain"
        assert metadata.created_at is not None

    def test_create_metadata_with_optional_fields(self):
        """Should create metadata with optional fields."""
        metadata = ArtifactMetadata(
            artifact_id="art-002",
            artifact_type=ArtifactType.LOG_FILE,
            storage_type=ArtifactStorageType.FILE_LOCAL,
            created_by="ci-workflow",
            run_id="run-001",
            name="CI Log",
            pr_number=123,
            description="CI workflow log file",
            size_bytes=1024,
            content_type="text/plain",
            checksum="sha256:abc123",
            tags=["ci", "log"],
            retention_days=30,
        )

        assert metadata.pr_number == 123
        assert metadata.description == "CI workflow log file"
        assert metadata.size_bytes == 1024
        assert metadata.content_type == "text/plain"
        assert metadata.checksum == "sha256:abc123"
        assert "ci" in metadata.tags
        assert metadata.retention_days == 30


class TestArtifactReference:
    """Tests for ArtifactReference model."""

    def test_create_file_reference(self):
        """Should create file reference."""
        ref = ArtifactReference(
            artifact_id="art-001",
            storage_type=ArtifactStorageType.FILE_LOCAL,
            location="/var/artifacts/run-001/evidence.json",
        )

        assert ref.location == "/var/artifacts/run-001/evidence.json"
        assert ref.inline_content is None

    def test_create_inline_reference(self):
        """Should create inline JSON reference."""
        ref = ArtifactReference(
            artifact_id="art-002",
            storage_type=ArtifactStorageType.INLINE_JSON,
            location="inline://art-002",
            inline_content={"key": "value", "count": 42},
        )

        assert ref.inline_content == {"key": "value", "count": 42}

    def test_create_link_reference(self):
        """Should create external link reference."""
        ref = ArtifactReference(
            artifact_id="art-003",
            storage_type=ArtifactStorageType.EXTERNAL_LINK,
            location="https://github.com/org/repo/actions/runs/12345",
        )

        assert "github.com" in ref.location


class TestArtifactRegistryEntry:
    """Tests for ArtifactRegistryEntry model."""

    def test_create_entry(self):
        """Should create complete registry entry."""
        metadata = ArtifactMetadata(
            artifact_id="art-001",
            artifact_type=ArtifactType.EVIDENCE_CHAIN,
            storage_type=ArtifactStorageType.INLINE_JSON,
            created_by="system",
            run_id="run-001",
            name="Evidence Chain",
        )
        reference = ArtifactReference(
            artifact_id="art-001",
            storage_type=ArtifactStorageType.INLINE_JSON,
            location="inline://art-001",
            inline_content={"evidence": []},
        )

        entry = ArtifactRegistryEntry(metadata=metadata, reference=reference)

        assert entry.metadata.artifact_id == "art-001"
        assert entry.reference.location == "inline://art-001"

    def test_get_artifact_path_for_file(self):
        """Should return file path."""
        metadata = ArtifactMetadata(
            artifact_id="art-001",
            artifact_type=ArtifactType.LOG_FILE,
            storage_type=ArtifactStorageType.FILE_LOCAL,
            created_by="system",
            run_id="run-001",
            name="Log",
        )
        reference = ArtifactReference(
            artifact_id="art-001",
            storage_type=ArtifactStorageType.FILE_LOCAL,
            location="/var/logs/run.log",
        )

        entry = ArtifactRegistryEntry(metadata=metadata, reference=reference)

        assert entry.get_artifact_path() == "/var/logs/run.log"

    def test_get_artifact_path_for_inline(self):
        """Should return inline URI for inline content."""
        metadata = ArtifactMetadata(
            artifact_id="art-001",
            artifact_type=ArtifactType.EVIDENCE_CHAIN,
            storage_type=ArtifactStorageType.INLINE_JSON,
            created_by="system",
            run_id="run-001",
            name="Evidence",
        )
        reference = ArtifactReference(
            artifact_id="art-001",
            storage_type=ArtifactStorageType.INLINE_JSON,
            location="inline://art-001",
            inline_content={"data": "test"},
        )

        entry = ArtifactRegistryEntry(metadata=metadata, reference=reference)

        assert entry.get_artifact_path() == "inline://art-001"

    def test_is_accessible_for_inline(self):
        """Should check accessibility for inline content."""
        metadata = ArtifactMetadata(
            artifact_id="art-001",
            artifact_type=ArtifactType.EVIDENCE_CHAIN,
            storage_type=ArtifactStorageType.INLINE_JSON,
            created_by="system",
            run_id="run-001",
            name="Evidence",
        )

        # With content
        ref_with_content = ArtifactReference(
            artifact_id="art-001",
            storage_type=ArtifactStorageType.INLINE_JSON,
            location="inline://art-001",
            inline_content={"data": "test"},
        )
        entry_with = ArtifactRegistryEntry(metadata=metadata, reference=ref_with_content)
        assert entry_with.is_accessible() is True

        # Without content
        ref_without_content = ArtifactReference(
            artifact_id="art-002",
            storage_type=ArtifactStorageType.INLINE_JSON,
            location="inline://art-002",
        )
        metadata2 = ArtifactMetadata(
            artifact_id="art-002",
            artifact_type=ArtifactType.EVIDENCE_CHAIN,
            storage_type=ArtifactStorageType.INLINE_JSON,
            created_by="system",
            run_id="run-001",
            name="Evidence",
        )
        entry_without = ArtifactRegistryEntry(
            metadata=metadata2, reference=ref_without_content
        )
        assert entry_without.is_accessible() is False


class TestArtifactRegistry:
    """Tests for ArtifactRegistry model."""

    def test_create_empty_registry(self):
        """Should create empty registry."""
        registry = ArtifactRegistry(registry_id="reg-001")

        assert registry.registry_id == "reg-001"
        assert len(registry.entries) == 0
        assert registry.get_artifact_count() == 0

    def test_register_artifact(self):
        """Should register artifact and return ID."""
        registry = ArtifactRegistry(registry_id="reg-001")

        metadata = ArtifactMetadata(
            artifact_id="art-001",
            artifact_type=ArtifactType.EVIDENCE_CHAIN,
            storage_type=ArtifactStorageType.INLINE_JSON,
            created_by="system",
            run_id="run-001",
            name="Evidence",
        )
        reference = ArtifactReference(
            artifact_id="art-001",
            storage_type=ArtifactStorageType.INLINE_JSON,
            location="inline://art-001",
            inline_content={},
        )
        entry = ArtifactRegistryEntry(metadata=metadata, reference=reference)

        artifact_id = registry.register_artifact(entry)

        assert artifact_id == "art-001"
        assert registry.get_artifact_count() == 1

    def test_get_artifact_by_id(self):
        """Should retrieve artifact by ID."""
        registry = ArtifactRegistry(registry_id="reg-001")

        metadata = ArtifactMetadata(
            artifact_id="art-001",
            artifact_type=ArtifactType.EVIDENCE_CHAIN,
            storage_type=ArtifactStorageType.INLINE_JSON,
            created_by="system",
            run_id="run-001",
            name="Evidence",
        )
        reference = ArtifactReference(
            artifact_id="art-001",
            storage_type=ArtifactStorageType.INLINE_JSON,
            location="inline://art-001",
            inline_content={"test": "data"},
        )
        entry = ArtifactRegistryEntry(metadata=metadata, reference=reference)
        registry.register_artifact(entry)

        retrieved = registry.get_artifact(artifact_id="art-001")

        assert retrieved is not None
        assert retrieved.metadata.artifact_id == "art-001"

        # Non-existent
        missing = registry.get_artifact("non-existent")
        assert missing is None

    def test_get_artifacts_by_run(self):
        """Should retrieve artifacts by run ID."""
        registry = ArtifactRegistry(registry_id="reg-001")

        # Add artifacts for run-001
        for i in range(3):
            metadata = ArtifactMetadata(
                artifact_id=f"art-{i}",
                artifact_type=ArtifactType.EVIDENCE_CHAIN,
                storage_type=ArtifactStorageType.INLINE_JSON,
                created_by="system",
                run_id="run-001",
                name=f"Evidence {i}",
            )
            reference = ArtifactReference(
                artifact_id=f"art-{i}",
                storage_type=ArtifactStorageType.INLINE_JSON,
                location=f"inline://art-{i}",
                inline_content={},
            )
            registry.register_artifact(
                ArtifactRegistryEntry(metadata=metadata, reference=reference)
            )

        # Add artifact for run-002
        metadata = ArtifactMetadata(
            artifact_id="art-other",
            artifact_type=ArtifactType.EVIDENCE_CHAIN,
            storage_type=ArtifactStorageType.INLINE_JSON,
            created_by="system",
            run_id="run-002",
            name="Other",
        )
        reference = ArtifactReference(
            artifact_id="art-other",
            storage_type=ArtifactStorageType.INLINE_JSON,
            location="inline://art-other",
            inline_content={},
        )
        registry.register_artifact(
            ArtifactRegistryEntry(metadata=metadata, reference=reference)
        )

        run_001_artifacts = registry.get_artifacts_by_run("run-001")
        assert len(run_001_artifacts) == 3

        run_002_artifacts = registry.get_artifacts_by_run("run-002")
        assert len(run_002_artifacts) == 1

    def test_get_artifacts_by_pr(self):
        """Should retrieve artifacts by PR number."""
        registry = ArtifactRegistry(registry_id="reg-001")

        # Add artifact with PR number
        metadata = ArtifactMetadata(
            artifact_id="art-001",
            artifact_type=ArtifactType.PR_EVIDENCE,
            storage_type=ArtifactStorageType.INLINE_JSON,
            created_by="system",
            run_id="run-001",
            name="PR Evidence",
            pr_number=123,
        )
        reference = ArtifactReference(
            artifact_id="art-001",
            storage_type=ArtifactStorageType.INLINE_JSON,
            location="inline://art-001",
            inline_content={},
        )
        registry.register_artifact(
            ArtifactRegistryEntry(metadata=metadata, reference=reference)
        )

        # Add artifact without PR number
        metadata2 = ArtifactMetadata(
            artifact_id="art-002",
            artifact_type=ArtifactType.EVIDENCE_CHAIN,
            storage_type=ArtifactStorageType.INLINE_JSON,
            created_by="system",
            run_id="run-001",
            name="General Evidence",
        )
        reference2 = ArtifactReference(
            artifact_id="art-002",
            storage_type=ArtifactStorageType.INLINE_JSON,
            location="inline://art-002",
            inline_content={},
        )
        registry.register_artifact(
            ArtifactRegistryEntry(metadata=metadata2, reference=reference2)
        )

        pr_artifacts = registry.get_artifacts_by_pr(123)
        assert len(pr_artifacts) == 1
        assert pr_artifacts[0].metadata.pr_number == 123

    def test_get_artifacts_by_type(self):
        """Should retrieve artifacts by type."""
        registry = ArtifactRegistry(registry_id="reg-001")

        # Add evidence artifact
        metadata1 = ArtifactMetadata(
            artifact_id="art-001",
            artifact_type=ArtifactType.EVIDENCE_CHAIN,
            storage_type=ArtifactStorageType.INLINE_JSON,
            created_by="system",
            run_id="run-001",
            name="Evidence",
        )
        reference1 = ArtifactReference(
            artifact_id="art-001",
            storage_type=ArtifactStorageType.INLINE_JSON,
            location="inline://art-001",
            inline_content={},
        )
        registry.register_artifact(
            ArtifactRegistryEntry(metadata=metadata1, reference=reference1)
        )

        # Add knowledge artifact
        metadata2 = ArtifactMetadata(
            artifact_id="art-002",
            artifact_type=ArtifactType.KNOWLEDGE_BUNDLE,
            storage_type=ArtifactStorageType.INLINE_JSON,
            created_by="system",
            run_id="run-001",
            name="Knowledge",
        )
        reference2 = ArtifactReference(
            artifact_id="art-002",
            storage_type=ArtifactStorageType.INLINE_JSON,
            location="inline://art-002",
            inline_content={},
        )
        registry.register_artifact(
            ArtifactRegistryEntry(metadata=metadata2, reference=reference2)
        )

        evidence = registry.get_artifacts_by_type(ArtifactType.EVIDENCE_CHAIN)
        assert len(evidence) == 1

        knowledge = registry.get_artifacts_by_type(ArtifactType.KNOWLEDGE_BUNDLE)
        assert len(knowledge) == 1

    def test_get_run_summary(self):
        """Should generate run summary (enables 'view run and know what was done')."""
        registry = ArtifactRegistry(registry_id="reg-001")

        # Add various artifacts for a run
        artifacts_data = [
            ("art-001", ArtifactType.EVIDENCE_CHAIN, "Evidence Chain"),
            ("art-002", ArtifactType.PR_EVIDENCE, "PR Evidence"),
            ("art-003", ArtifactType.CI_EVIDENCE, "CI Evidence"),
            ("art-004", ArtifactType.KNOWLEDGE_BUNDLE, "Knowledge Bundle"),
        ]

        for art_id, art_type, name in artifacts_data:
            metadata = ArtifactMetadata(
                artifact_id=art_id,
                artifact_type=art_type,
                storage_type=ArtifactStorageType.INLINE_JSON,
                created_by="system",
                run_id="run-001",
                name=name,
            )
            reference = ArtifactReference(
                artifact_id=art_id,
                storage_type=ArtifactStorageType.INLINE_JSON,
                location=f"inline://{art_id}",
                inline_content={},
            )
            registry.register_artifact(
                ArtifactRegistryEntry(metadata=metadata, reference=reference)
            )

        summary = registry.get_run_summary("run-001")

        assert summary["run_id"] == "run-001"
        assert summary["total_artifacts"] == 4
        assert "evidence_chain" in summary["artifacts_by_type"]
        assert "pr_evidence" in summary["artifacts_by_type"]
        assert "ci_evidence" in summary["artifacts_by_type"]
        assert "knowledge_bundle" in summary["artifacts_by_type"]
        assert len(summary["artifact_list"]) == 4

    def test_delete_artifact(self):
        """Should delete artifact from registry."""
        registry = ArtifactRegistry(registry_id="reg-001")

        metadata = ArtifactMetadata(
            artifact_id="art-001",
            artifact_type=ArtifactType.EVIDENCE_CHAIN,
            storage_type=ArtifactStorageType.INLINE_JSON,
            created_by="system",
            run_id="run-001",
            name="Evidence",
        )
        reference = ArtifactReference(
            artifact_id="art-001",
            storage_type=ArtifactStorageType.INLINE_JSON,
            location="inline://art-001",
            inline_content={},
        )
        registry.register_artifact(
            ArtifactRegistryEntry(metadata=metadata, reference=reference)
        )

        assert registry.get_artifact_count() == 1

        deleted = registry.delete_artifact("art-001")
        assert deleted is True
        assert registry.get_artifact_count() == 0

        # Delete non-existent
        not_deleted = registry.delete_artifact("non-existent")
        assert not_deleted is False


class TestHelperFunctions:
    """Tests for artifact creation helper functions."""

    def test_create_evidence_artifact(self):
        """Should create evidence artifact entry."""
        evidence_data = {
            "evidence_id": "ev-001",
            "evidence_type": "pr_created",
            "summary": "PR created",
        }

        entry = create_evidence_artifact(
            evidence_data=evidence_data,
            run_id="run-001",
            artifact_id="art-001",
            created_by="system",
            pr_number=123,
        )

        assert entry.metadata.artifact_id == "art-001"
        assert entry.metadata.artifact_type == ArtifactType.EVIDENCE_CHAIN
        assert entry.metadata.run_id == "run-001"
        assert entry.metadata.pr_number == 123
        assert entry.reference.inline_content == evidence_data
        assert "evidence" in entry.metadata.tags

    def test_create_knowledge_artifact(self):
        """Should create knowledge artifact entry."""
        knowledge_data = {
            "feature_name": "Feature X",
            "lessons": ["Lesson 1", "Lesson 2"],
        }

        entry = create_knowledge_artifact(
            knowledge_data=knowledge_data,
            run_id="run-001",
            artifact_id="art-001",
            created_by="system",
            artifact_type=ArtifactType.LESSONS_LEARNED,
            name="Feature X Lessons",
        )

        assert entry.metadata.artifact_type == ArtifactType.LESSONS_LEARNED
        assert entry.metadata.name == "Feature X Lessons"
        assert entry.reference.inline_content == knowledge_data
        assert "knowledge" in entry.metadata.tags

    def test_create_file_artifact(self):
        """Should create file-based artifact entry."""
        entry = create_file_artifact(
            file_path="/var/logs/ci.log",
            run_id="run-001",
            artifact_id="art-001",
            created_by="ci-workflow",
            artifact_type=ArtifactType.LOG_FILE,
            name="CI Log",
            size_bytes=1024,
            content_type="text/plain",
        )

        assert entry.metadata.artifact_type == ArtifactType.LOG_FILE
        assert entry.metadata.storage_type == ArtifactStorageType.FILE_LOCAL
        assert entry.metadata.size_bytes == 1024
        assert entry.reference.location == "/var/logs/ci.log"
        assert "file" in entry.metadata.tags

    def test_create_link_artifact(self):
        """Should create link-based artifact entry."""
        entry = create_link_artifact(
            url="https://github.com/org/repo/actions/runs/12345",
            run_id="run-001",
            artifact_id="art-001",
            created_by="system",
            artifact_type=ArtifactType.REPORT,
            name="CI Run",
            description="Link to CI workflow run",
        )

        assert entry.metadata.artifact_type == ArtifactType.REPORT
        assert entry.metadata.storage_type == ArtifactStorageType.EXTERNAL_LINK
        assert "github.com" in entry.reference.location
        assert entry.metadata.description == "Link to CI workflow run"
        assert "link" in entry.metadata.tags
