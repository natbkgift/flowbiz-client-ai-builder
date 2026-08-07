# AUTORUN_DECISIONS

Standing authorizations and execution defaults for FlowBiz AI Builder.

## AUTO_RUN Standing Defaults — v11

### 1. Merge Strategy
- Default automated merge method remains REBASE when repository rules permit.
- Repository rules take precedence when they require a different merge method.

### 2. Unknown Commit Handling
- If an exact commit cannot be attributed/resolved against the intended branch/PR, `CONTROLLED_HALT`.
- A new commit after Runner validation invalidates that validation for merge/release purposes.

### 3. CI / Checks Authority
- v11 authoritative CI/build evidence comes from **FlowBiz Runner** against an exact SHA.
- Legacy GitHub Actions may continue during transition as supplemental/non-authoritative checks.
- Autonomous operation must not depend on GitHub Actions availability, quota, workflow approval, or workflow token scope.
- Do not remove/disable legacy workflows until FlowBiz Runner parity is proven; this avoids a validation gap.
- Runner fix/retry loops are bounded. After the configured maximum attempts, `CONTROLLED_HALT` and preserve evidence.

### 4. Single-VPS Production Protection
- Production workload has priority over Runner workload.
- Initial Runner concurrency is 1.
- Runner jobs are ephemeral and must not use production database credentials.
- Resource pressure or unhealthy production state defers CI/build jobs rather than competing with production.

### 5. Production Mutation
- Production changes require auditable policy approval according to risk class.
- Deploy only validated exact main SHA or immutable release artifact.
- Backup/rollback readiness is required before risky mutation.
- Arbitrary model-generated shell/SSH is not an approved production execution path.

### 6. Evidence Discipline
- Every terminal run state must have timestamped evidence tied to project, exact SHA, run ID, and milestone.
- FlowBiz Runner / Control Plane evidence is canonical under v11.
- GitHub links may supplement evidence but are not required as the only CI/deployment proof.

### 7. 24/7 Autonomous Operation
- Approved low/medium-risk workflows may continue without repeated owner confirmation when all governing controls and evidence gates are satisfied.
- High-risk/destructive operations remain approval-gated.
- Unverifiable state always produces `CONTROLLED_HALT` rather than an inferred or guessed action.

## Authorization Log

| Date | Authorized By | Mode | Scope | Reason | Status |
| --- | --- | --- | --- | --- | --- |
| 2025-12-29 | natbkgift | GUIDED | PR-016 deferral | Architectural review required before re-implementation | ACTIVE |
| 2025-12-30 | natbkgift | STRICT | AUTO_RUN Standing Defaults v10 | Reduce routine confirmations; keep automation audit-safe | SUPERSEDED_BY_V11 |
| 2026-08-07 | natbkgift | STRICT | BLUEPRINT v11 / PR-18 | Single-VPS Autonomous Control Plane; 24/7; FlowBiz Runner authority; remove GitHub Actions dependency from target architecture; move Project Registry/Provisioner ahead of engineering-agent milestones | ACTIVE |
