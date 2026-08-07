# CONTROLS.md
## FlowBiz AI Builder — Control Framework (v11)

### 1. Control Objectives
Ensure:
- secure software delivery;
- traceable decision-making;
- prevention of unauthorized or unsafe automation;
- deterministic 24/7 operation;
- production protection in single-VPS mode;
- rollback readiness for production mutations.

### 2. Control Domains

#### 2.1 Planning Controls (Gate 0)
- PRD / DoD or equivalent execution intent exists.
- Acceptance criteria are defined.
- Test and deployment plans are documented.
- Project identity and exact repository/ref are resolved.
- Material ambiguity produces `CONTROLLED_HALT`.

#### 2.2 CI / Build Controls (Gate 1)
**Authoritative executor: FlowBiz Runner.**

Required controls where applicable:
- exact-SHA checkout;
- automated linting and tests;
- security/dependency scans;
- deterministic build;
- migration rehearsal in isolated test state;
- E2E/browser tests when configured;
- immutable CI evidence tied to run ID and exact SHA;
- artifact checksum when a release artifact is produced.

GitHub Actions is not an authoritative Gate 1 dependency in v11. Legacy GitHub Actions may remain during transition but cannot be the sole evidence source or production execution path.

#### 2.3 Staging / Rehearsal Controls (Gate 2)
- deploy PR/exact SHA to staging when staging exists, or execute an approved isolated rehearsal;
- smoke/regression checks;
- evidence collection;
- no production secrets in CI/rehearsal state.

#### 2.4 Production Controls (Gate 3)
**Authoritative coordinator: FlowBiz Control Plane / Production Manager.**

- production deploy targets an exact validated main SHA or immutable artifact;
- production preflight must pass;
- backup/rollback path must exist before risky mutation;
- migrations follow declared policy;
- release activation is controlled and auditable;
- automated health/smoke/public verification is required;
- verification failure triggers rollback or `CONTROLLED_HALT` according to policy;
- arbitrary model-generated shell is prohibited as a production control path.

#### 2.5 Learning Controls (Gate 4)
- post-run analysis;
- lessons learned;
- incident/root-cause records where needed;
- repeated-task automation suggestions;
- evidence of terminal run state.

### 3. Single-VPS Resource Controls
Production has priority over Runner workloads.

Initial baseline:
- Runner max concurrency = 1;
- Runner uses ephemeral job workspaces/containers;
- Runner checks CPU, memory, disk, and production health before heavy work;
- resource pressure defers queued CI instead of degrading production;
- Runner may not write to active production release directories;
- Runner may not use production database credentials.

### 4. Access & Security Controls
- least-privilege service identities;
- separation between Production, Control Plane, and Runner permissions;
- secrets referenced by identifier, not committed or embedded in manifests;
- production mutation available only through fixed, auditable operations;
- unrestricted `sudo`, unrestricted SSH execution, firewall mutation, SSH-key mutation, and arbitrary Nginx mutation are not exposed to AI tools;
- high-risk operations require explicit approval policy.

### 5. Concurrency & Safety Controls
- per-project locks;
- per-environment locks;
- idempotency keys for resumable operations;
- bounded retries;
- crash-safe persisted run state;
- duplicate execution protection;
- deterministic rollback target.

### 6. MCP / Tool Controls
MCP exposes semantic Control Plane operations rather than general shell access.

Allowed classes include:
- read/status;
- CI/build dispatch;
- deployment planning;
- approved controlled deployment;
- backup;
- logs/health;
- rollback.

High-risk operations are approval-gated. A tool equivalent to `run_shell(command)` or unrestricted `ssh_exec()` is prohibited.

### 7. GitHub Controls
GitHub remains Source Authority for repositories, branches, PRs, and exact SHAs.

GitHub Actions is optional/non-authoritative under v11. Repository rules and PR policy must not make GitHub Actions availability a required architectural dependency once FlowBiz Runner evidence is active.

During migration, legacy workflows may continue to run until Runner parity is proven; their presence does not grant them CI/deployment authority.

### 8. Control Effectiveness
Every mandatory control must be testable, observable, and auditable.

Canonical compliance is evaluated from governing documents plus FlowBiz Control Plane/Runner evidence. No single GitHub workflow name is a control by itself.
