"""Deterministic Control Plane Orchestrator foundation for FlowBiz AI Builder v11."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from packages.core.project_registry import ProjectRegistry
from packages.core.provisioner import Provisioner
from packages.core.schemas.control_plane import (
    ControlPlaneRun,
    ControlPlaneRunState,
    ProjectManifest,
    ProjectRecord,
    ProvisioningPlan,
)


class OrchestratorError(Exception):
    """Base orchestrator error."""


class RunNotFoundError(OrchestratorError):
    """Raised when a run ID is unknown."""


class InvalidRunTransitionError(OrchestratorError):
    """Raised when a state transition is not allowed."""


_ALLOWED_TRANSITIONS: dict[ControlPlaneRunState, set[ControlPlaneRunState]] = {
    ControlPlaneRunState.PLANNED: {
        ControlPlaneRunState.READY_FOR_CI,
        ControlPlaneRunState.BLOCKED,
        ControlPlaneRunState.FAILED,
    },
    ControlPlaneRunState.READY_FOR_CI: {
        ControlPlaneRunState.CI_RUNNING,
        ControlPlaneRunState.BLOCKED,
        ControlPlaneRunState.FAILED,
    },
    ControlPlaneRunState.CI_RUNNING: {
        ControlPlaneRunState.CI_PASSED,
        ControlPlaneRunState.BLOCKED,
        ControlPlaneRunState.FAILED,
    },
    ControlPlaneRunState.CI_PASSED: {
        ControlPlaneRunState.READY_FOR_RELEASE,
        ControlPlaneRunState.BLOCKED,
        ControlPlaneRunState.FAILED,
    },
    ControlPlaneRunState.READY_FOR_RELEASE: {
        ControlPlaneRunState.COMPLETED,
        ControlPlaneRunState.BLOCKED,
        ControlPlaneRunState.FAILED,
    },
    ControlPlaneRunState.COMPLETED: set(),
    ControlPlaneRunState.BLOCKED: set(),
    ControlPlaneRunState.FAILED: set(),
}


class ControlPlaneOrchestrator:
    """Coordinates pure PR-18 planning state without execution adapters.

    Later milestones connect Runner, host execution, Production Manager, and MCP.
    PR-18 deliberately has no method that accepts or executes a shell command.
    """

    def __init__(
        self,
        *,
        registry: ProjectRegistry | None = None,
        provisioner: Provisioner | None = None,
    ) -> None:
        self.registry = registry or ProjectRegistry()
        self.provisioner = provisioner or Provisioner()
        self._runs: dict[str, ControlPlaneRun] = {}

    def register_project(self, manifest: ProjectManifest) -> ProjectRecord:
        return self.registry.register(manifest)

    def plan_provisioning(self, project_id: str) -> ProvisioningPlan:
        record = self.registry.get(project_id)
        return self.provisioner.plan(record.manifest)

    def create_run(self, project_id: str, *, exact_sha: str | None = None) -> ControlPlaneRun:
        self.registry.get(project_id)
        run = ControlPlaneRun(
            run_id=f"run-{uuid4()}",
            project_id=project_id,
            exact_sha=exact_sha,
        )
        self._runs[run.run_id] = run
        return deepcopy(run)

    def get_run(self, run_id: str) -> ControlPlaneRun:
        try:
            return deepcopy(self._runs[run_id])
        except KeyError as exc:
            raise RunNotFoundError(run_id) from exc

    def transition(
        self,
        run_id: str,
        target: ControlPlaneRunState,
        *,
        reason: str | None = None,
    ) -> ControlPlaneRun:
        current = self._runs.get(run_id)
        if current is None:
            raise RunNotFoundError(run_id)

        if target not in _ALLOWED_TRANSITIONS[current.state]:
            raise InvalidRunTransitionError(f"{current.state.value} -> {target.value}")

        if target in {
            ControlPlaneRunState.CI_RUNNING,
            ControlPlaneRunState.CI_PASSED,
            ControlPlaneRunState.READY_FOR_RELEASE,
            ControlPlaneRunState.COMPLETED,
        } and current.exact_sha is None:
            raise InvalidRunTransitionError(
                f"exact SHA required before transition to {target.value}"
            )

        updated = current.model_copy(
            update={
                "state": target,
                "reason": reason,
                "updated_at": datetime.now(timezone.utc),
            }
        )
        self._runs[run_id] = updated
        return deepcopy(updated)


__all__ = [
    "ControlPlaneOrchestrator",
    "InvalidRunTransitionError",
    "OrchestratorError",
    "RunNotFoundError",
]
