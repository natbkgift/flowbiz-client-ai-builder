"""In-memory Project Registry foundation for FlowBiz AI Builder v11.

Persistence is deliberately deferred. PR-18 establishes deterministic registry
semantics and optimistic generation checks without host side effects.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

from packages.core.schemas.control_plane import ProjectManifest, ProjectRecord


class ProjectRegistryError(Exception):
    """Base registry error."""


class ProjectAlreadyExistsError(ProjectRegistryError):
    """Raised when a project ID is registered twice."""


class ProjectNotFoundError(ProjectRegistryError):
    """Raised when a project ID does not exist."""


class ProjectGenerationConflictError(ProjectRegistryError):
    """Raised when optimistic generation does not match."""


class ProjectRegistry:
    """Deterministic registry with copy-on-read semantics."""

    def __init__(self) -> None:
        self._records: dict[str, ProjectRecord] = {}

    def register(self, manifest: ProjectManifest) -> ProjectRecord:
        if manifest.project_id in self._records:
            raise ProjectAlreadyExistsError(manifest.project_id)

        record = ProjectRecord(manifest=manifest)
        self._records[manifest.project_id] = record
        return deepcopy(record)

    def get(self, project_id: str) -> ProjectRecord:
        try:
            return deepcopy(self._records[project_id])
        except KeyError as exc:
            raise ProjectNotFoundError(project_id) from exc

    def list(self) -> list[ProjectRecord]:
        return [deepcopy(self._records[key]) for key in sorted(self._records)]

    def update(
        self,
        manifest: ProjectManifest,
        *,
        expected_generation: int,
    ) -> ProjectRecord:
        current = self._records.get(manifest.project_id)
        if current is None:
            raise ProjectNotFoundError(manifest.project_id)
        if current.generation != expected_generation:
            raise ProjectGenerationConflictError(
                f"expected generation {expected_generation}, current {current.generation}"
            )

        updated = ProjectRecord(
            manifest=manifest,
            generation=current.generation + 1,
            created_at=current.created_at,
            updated_at=datetime.now(timezone.utc),
        )
        self._records[manifest.project_id] = updated
        return deepcopy(updated)


__all__ = [
    "ProjectAlreadyExistsError",
    "ProjectGenerationConflictError",
    "ProjectNotFoundError",
    "ProjectRegistry",
    "ProjectRegistryError",
]
