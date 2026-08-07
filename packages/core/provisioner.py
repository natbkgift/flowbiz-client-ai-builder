"""Plan-only Provisioner foundation for FlowBiz AI Builder v11.

PR-18 MUST NOT mutate the VPS. This module converts a validated ProjectManifest
into semantic provisioning steps only. Execution adapters arrive in later milestones.
"""

from __future__ import annotations

from uuid import uuid4

from packages.core.schemas.control_plane import (
    ProjectManifest,
    ProvisioningOperation,
    ProvisioningPlan,
    ProvisioningStep,
)


class Provisioner:
    """Build deterministic semantic plans without shell command generation."""

    def plan(self, manifest: ProjectManifest) -> ProvisioningPlan:
        steps: list[ProvisioningStep] = [
            ProvisioningStep(
                step_id="01-project-root",
                operation=ProvisioningOperation.ENSURE_PROJECT_ROOT,
                target=manifest.runtime.root,
            ),
            ProvisioningStep(
                step_id="02-release-layout",
                operation=ProvisioningOperation.ENSURE_RELEASE_LAYOUT,
                target=f"{manifest.runtime.root.rstrip('/')}/releases",
            ),
            ProvisioningStep(
                step_id="03-shared-layout",
                operation=ProvisioningOperation.ENSURE_SHARED_LAYOUT,
                target=f"{manifest.runtime.root.rstrip('/')}/shared",
            ),
        ]

        for index, service in enumerate(manifest.services, start=10):
            steps.append(
                ProvisioningStep(
                    step_id=f"{index:02d}-service-{service}",
                    operation=ProvisioningOperation.DECLARE_SERVICE,
                    target=service,
                    risk_class="medium",
                )
            )

        steps.extend(
            [
                ProvisioningStep(
                    step_id="90-health",
                    operation=ProvisioningOperation.DECLARE_HEALTH_CHECK,
                    target=manifest.project_id,
                ),
                ProvisioningStep(
                    step_id="91-backup",
                    operation=ProvisioningOperation.DECLARE_BACKUP_POLICY,
                    target=manifest.project_id,
                    risk_class="medium",
                ),
            ]
        )

        return ProvisioningPlan(
            plan_id=f"provision-{uuid4()}",
            project_id=manifest.project_id,
            infrastructure_mode=manifest.infrastructure_mode,
            steps=steps,
        )


__all__ = ["Provisioner"]
