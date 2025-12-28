"""Tests for Artifact Registry v1."""

import pytest

from packages.core.schemas.artifact_registry import (
    ArtifactRegistry,
    ArtifactType,
    create_file_artifact,
    create_link_artifact,
)


class TestArtifactRegistry:
    def test_add_and_get_artifact(self):
        registry = ArtifactRegistry()
        artifact = create_file_artifact(
            run_id="run-001", artifact_id="a-1", path="artifacts/report.md", label="report"
        )

        registry.add(artifact)
        fetched = registry.get("a-1")

        assert fetched.artifact_id == "a-1"
        assert fetched.run_id == "run-001"
        assert fetched.artifact_type == ArtifactType.FILE
        assert fetched.uri == "artifacts/report.md"

    def test_add_duplicate_artifact_id_raises(self):
        registry = ArtifactRegistry()
        registry.add(
            create_link_artifact(
                run_id="run-001", artifact_id="dup", url="https://example.com", label="link"
            )
        )

        with pytest.raises(ValueError):
            registry.add(
                create_link_artifact(
                    run_id="run-001",
                    artifact_id="dup",
                    url="https://example.com/2",
                    label="link2",
                )
            )

    def test_list_by_run_filters_correctly(self):
        registry = ArtifactRegistry()
        registry.add(create_file_artifact(run_id="run-001", artifact_id="a-1", path="a.txt"))
        registry.add(create_file_artifact(run_id="run-002", artifact_id="a-2", path="b.txt"))
        registry.add(create_link_artifact(run_id="run-001", artifact_id="a-3", url="https://x"))

        run_1 = registry.list_by_run("run-001")
        assert {a.artifact_id for a in run_1} == {"a-1", "a-3"}

    def test_get_run_summary_counts_types(self):
        registry = ArtifactRegistry()
        registry.add(create_file_artifact(run_id="run-003", artifact_id="f1", path="a.txt"))
        registry.add(create_file_artifact(run_id="run-003", artifact_id="f2", path="b.txt"))
        registry.add(create_link_artifact(run_id="run-003", artifact_id="l1", url="https://x"))

        summary = registry.get_run_summary("run-003")
        assert summary["run_id"] == "run-003"
        assert summary["total"] == 3
        assert summary["by_type"] == {"file": 2, "link": 1}
        assert set(summary["artifact_ids"]) == {"f1", "f2", "l1"}

    def test_get_nonexistent_artifact_raises_keyerror(self):
        registry = ArtifactRegistry()
        registry.add(create_file_artifact(run_id="run-001", artifact_id="a-1", path="a.txt"))

        with pytest.raises(KeyError):
            registry.get("nonexistent-id")
