from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.orchestrator import (
    ControlPlaneOrchestrator,
    InvalidRunTransitionError,
)
from packages.core.project_registry import (
    ProjectAlreadyExistsError,
    ProjectGenerationConflictError,
    ProjectRegistry,
)
from packages.core.provisioner import Provisioner
from packages.core.schemas.control_plane import (
    ControlPlaneRunState,
    ProjectManifest,
    ProjectMode,
)


SHA = "a" * 40


def make_manifest(**overrides) -> ProjectManifest:
    payload = {
        "project_id": "amp-template",
        "mode": ProjectMode.LEGACY,
        "repository": {"full_name": "natbkgift/amp-template"},
        "runtime": {"root": "/opt/flowbiz/clients/amp-template"},
        "services": ["web", "api", "postgres"],
    }
    payload.update(overrides)
    return ProjectManifest.model_validate(payload)


def test_single_vps_manifest_enforces_runner_isolation_baseline() -> None:
    manifest = make_manifest()
    assert manifest.runner.max_concurrency == 1
    assert manifest.runner.ephemeral_jobs is True
    assert manifest.runner.production_guard is True
    assert manifest.release.exact_sha is True
    assert manifest.release.immutable is True
    assert manifest.release.rollback is True

    with pytest.raises(ValidationError):
        make_manifest(runner={"max_concurrency": 2})


def test_manifest_rejects_duplicate_services() -> None:
    with pytest.raises(ValidationError):
        make_manifest(services=["web", "web"])


def test_project_registry_is_deterministic_and_generation_checked() -> None:
    registry = ProjectRegistry()
    manifest = make_manifest()

    record = registry.register(manifest)
    assert record.generation == 1
    assert registry.get("amp-template").manifest.repository.full_name == "natbkgift/amp-template"

    with pytest.raises(ProjectAlreadyExistsError):
        registry.register(manifest)

    updated_manifest = manifest.model_copy(update={"services": ["web", "api"]})
    updated = registry.update(updated_manifest, expected_generation=1)
    assert updated.generation == 2

    with pytest.raises(ProjectGenerationConflictError):
        registry.update(updated_manifest, expected_generation=1)


def test_project_registry_isolates_internal_state_from_caller_mutation() -> None:
    registry = ProjectRegistry()
    manifest = make_manifest()
    registry.register(manifest)

    manifest.services.append("worker")

    stored = registry.get("amp-template")
    assert stored.manifest.services == ["web", "api", "postgres"]


def test_provisioner_is_plan_only_deterministic_and_never_grants_execution() -> None:
    provisioner = Provisioner()
    manifest = make_manifest()

    first = provisioner.plan(manifest)
    second = provisioner.plan(manifest)

    assert first.project_id == "amp-template"
    assert first.plan_only is True
    assert first.execution_permitted is False
    assert first.steps
    assert all(step.target for step in first.steps)
    assert first.plan_id == second.plan_id
    assert first.steps == second.steps


def test_orchestrator_requires_exact_sha_before_ci_execution_states() -> None:
    orchestrator = ControlPlaneOrchestrator()
    orchestrator.register_project(make_manifest())
    run = orchestrator.create_run("amp-template")

    run = orchestrator.transition(run.run_id, ControlPlaneRunState.READY_FOR_CI)
    with pytest.raises(InvalidRunTransitionError):
        orchestrator.transition(run.run_id, ControlPlaneRunState.CI_RUNNING)


def test_orchestrator_enforces_forward_state_machine() -> None:
    orchestrator = ControlPlaneOrchestrator()
    orchestrator.register_project(make_manifest())
    run = orchestrator.create_run("amp-template", exact_sha=SHA)

    for state in (
        ControlPlaneRunState.READY_FOR_CI,
        ControlPlaneRunState.CI_RUNNING,
        ControlPlaneRunState.CI_PASSED,
        ControlPlaneRunState.READY_FOR_RELEASE,
        ControlPlaneRunState.COMPLETED,
    ):
        run = orchestrator.transition(run.run_id, state)

    assert run.state == ControlPlaneRunState.COMPLETED

    with pytest.raises(InvalidRunTransitionError):
        orchestrator.transition(run.run_id, ControlPlaneRunState.READY_FOR_CI)


def test_orchestrator_can_plan_registered_project_without_host_mutation() -> None:
    orchestrator = ControlPlaneOrchestrator()
    orchestrator.register_project(make_manifest())

    plan = orchestrator.plan_provisioning("amp-template")
    assert plan.plan_only is True
    assert plan.execution_permitted is False
