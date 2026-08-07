# FlowBiz AI Builder v11 — Single-VPS Autonomous Control Plane

**Status:** Owner-authorized architecture baseline  
**Effective date:** 2026-08-07  
**Current milestone:** PR-18 — Control Plane Orchestrator Foundation  
**Supersedes:** BLUEPRINT v10.3 milestone order after PR-17

FlowBiz AI Builder v11 evolves the project from a governance-heavy template builder into a **24/7 autonomous project, CI, release, deployment, and operations control plane**.

The system must be able to create new projects, adopt existing projects, customize source code and runtime topology, validate exact Git commits, build immutable release artifacts, deploy safely, verify production, and roll back when verification fails.

The current infrastructure target is **one shared VPS**. The architecture MUST therefore isolate Production, Control Plane, and CI Runner workloads logically and by permission so that the same software can later move to multiple hosts without redesigning the contracts.

---

## 0. Governing Documents and Precedence

This Blueprint is enforced together with:

1. `POLICY.md` — governance and engineering policy
2. `CONTROLS.md` — control objectives and mandatory gates
3. `BLUEPRINT.md` — architecture, milestones, and dependency order
4. `EVIDENCE.md` — evidence requirements
5. Runtime prompts, runbooks, manifests, and implementation conventions

If a lower-precedence document conflicts with a higher-precedence document, the higher-precedence document controls.

A failure to prove a required control causes `CONTROLLED_HALT`.

---

## 1. Mission

Build a production-capable system that can operate continuously with minimal human intervention while preserving deterministic execution, least privilege, evidence, rollback, and explicit approval for high-risk actions.

The target lifecycle is:

```text
Request / Event
    ↓
Discovery + Plan
    ↓
GitHub branch / PR / exact SHA
    ↓
FlowBiz Runner validation
    ↓
Immutable artifact + evidence
    ↓
Production plan + approval policy
    ↓
Backup / migration / deploy
    ↓
Health / smoke / verification
    ↓
PASS → complete
FAIL → rollback + incident evidence
    ↓
Learning / improvement
```

The system must support both:

- **new projects** created from approved templates or custom manifests; and
- **existing/legacy projects** imported into the registry without rebuilding them from scratch.

---

## 2. Authority Model

FlowBiz v11 separates authority by responsibility.

### 2.1 GitHub — Source Authority

GitHub is the source of truth for:

- repositories;
- branches;
- Pull Requests;
- reviewed source changes;
- commit SHAs;
- source history and release metadata references.

GitHub is **not** the CI execution authority and is **not** the production deployment authority.

### 2.2 FlowBiz Runner — CI / Build Authority

FlowBiz Runner is authoritative for:

- linting;
- unit/integration tests;
- security and dependency checks;
- migration rehearsal;
- browser/E2E tests when configured;
- deterministic builds;
- immutable release artifact creation;
- checksums, SBOM/attestation where configured;
- CI evidence generation.

### 2.3 FlowBiz Control Plane — Decision + Execution Authority

The Control Plane owns:

- orchestration;
- project registry;
- project manifests;
- provisioning plans;
- job queue and execution state;
- policy and approval decisions;
- CI dispatch;
- release promotion decisions;
- production deployment and rollback coordination;
- MCP/API tool exposure;
- audit/evidence indexing.

### 2.4 Production VPS — Runtime Authority

The Production lane owns only runtime state:

- active releases;
- production services;
- production databases;
- production workers;
- system-level Nginx;
- runtime health and monitoring.

Production MUST NOT be the general build workspace.

---

## 3. GitHub Actions Independence

**FlowBiz AI Builder v11 MUST NOT depend on GitHub Actions for autonomous operation.**

Architecture and release decisions must remain functional when GitHub Actions is unavailable, disabled, quota-limited, awaiting workflow approval, or lacking workflow token scope.

GitHub Actions workflows that remain in the repository during migration are classified as:

```text
LEGACY / OPTIONAL / NON-AUTHORITATIVE
```

They MAY provide additional checks or visibility during transition, but they MUST NOT be:

- the sole CI evidence source;
- required for Control Plane job execution;
- the production deploy mechanism;
- the artifact transfer authority;
- the rollback mechanism;
- the only way to satisfy a v11 gate.

Existing workflows MUST NOT receive new production responsibilities.

### Transition rule

Do not disable/remove legacy GitHub Actions until FlowBiz Runner proves equivalent or stronger lint/test/security evidence for the repository. This prevents a temporary validation gap while still removing GitHub Actions from the target architecture.

---

## 4. Single-VPS Architecture

Current infrastructure mode:

```yaml
infrastructure:
  mode: single-vps
  autonomous: true
  availability_target: 24x7
```

The single VPS is split into three logical lanes.

```text
                     ONE VPS
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
  Production Lane   Control Plane     Runner Lane
  critical priority  orchestration     low priority
        │               │                │
  client apps       API / MCP          ephemeral jobs
  databases         registry           tests / build
  workers           queue              security / E2E
  nginx             policy             artifacts/evidence
```

### 4.1 Required directory separation

Reference layout:

```text
/opt/flowbiz/
├── control-plane/
│   ├── builder/
│   ├── mcp/
│   ├── state/
│   └── queue/
├── ci/
│   ├── jobs/
│   ├── cache/
│   ├── artifacts/
│   └── evidence/
├── clients/
│   └── <project>/
│       ├── releases/
│       ├── current -> releases/<release-id>/
│       └── shared/
└── backups/
```

### 4.2 Required workload priority

Production has priority over CI.

Initial Runner policy:

```yaml
runner:
  max_concurrent_jobs: 1
  ephemeral_jobs: true
  production_guard: true
```

The Runner MUST defer new jobs when resource guard conditions indicate unacceptable CPU, memory, disk, or production-health pressure.

---

## 5. Security and Permission Boundaries

The system MUST use least privilege.

Recommended service identities:

```text
flowbiz-prod
flowbiz-control
flowbiz-runner
```

The Runner MUST NOT have unrestricted access to:

- production `.env` files;
- production database credentials;
- arbitrary production filesystem writes;
- unrestricted `systemctl`;
- arbitrary Nginx changes;
- firewall changes;
- SSH key management;
- arbitrary shell execution supplied by an AI model.

Production-changing operations MUST flow through fixed Control Plane operations with validation, policy, audit records, and rollback requirements.

---

## 6. Project Model and Customization

Templates are starting points, not cages.

Every managed project is represented by a **Project Manifest** plus observed runtime state.

Supported project modes:

```text
STANDARD  — approved template, standard runtime
CUSTOM    — customized code/services within managed contracts
ADVANCED  — custom container/build/runtime topology
LEGACY    — existing project adopted into the Control Plane
```

A project may customize:

- frontend/backend code;
- APIs and business logic;
- database schema;
- workers and schedulers;
- Redis/queues;
- AI agents;
- container topology;
- health checks;
- build/test commands;
- deployment strategy where policy permits.

### Source-code rule

Normal source changes MUST occur through GitHub branches/PRs and exact commits.

Do not treat direct editing of active production release files as a normal customization path.

---

## 7. Project Manifest Contract

Illustrative v11 manifest:

```yaml
project:
  id: amp-template
  mode: legacy

repository:
  provider: github
  full_name: natbkgift/amp-template
  default_branch: main

runtime:
  host: flowbiz-vps
  root: /opt/flowbiz/clients/amp-template

services:
  - web
  - api
  - postgres

ci:
  authority: flowbiz-runner
  ephemeral: true
  max_concurrency: 1

release:
  exact_sha: true
  immutable: true
  rollback: true

health:
  required: true

customization:
  source_code: true
  database: true
  services: true
  infrastructure: controlled
```

The manifest is desired state. The Control Plane MUST compare desired state with observed state before mutating production.

---

## 8. Core Control Plane Components

### 8.1 Orchestrator

The Orchestrator owns state transitions and dependency order. It does not directly execute arbitrary shell commands.

Responsibilities:

- accept requests/events;
- resolve project;
- acquire project/environment locks;
- produce an execution plan;
- dispatch to approved adapters;
- track run state;
- enforce gates;
- record evidence references;
- halt on unverifiable conditions;
- trigger rollback when required.

### 8.2 Project Registry

Canonical inventory of managed projects and their manifests.

It MUST support:

- create/register project;
- import existing project;
- read/update manifest under policy;
- map GitHub repository to runtime project;
- store environment and health metadata;
- prevent duplicate/conflicting project identities.

### 8.3 Provisioner

The Provisioner converts a Project Manifest into a deterministic provisioning plan.

It MUST begin as **plan-only**. Real mutation is enabled only after policy, adapter, and rollback contracts exist.

Examples of planned resources:

- project directory structure;
- service definitions;
- environment references;
- database/service requirements;
- runtime users/permissions;
- domain/Nginx requirements;
- health checks;
- backup requirements.

### 8.4 FlowBiz Runner

The Runner executes isolated CI/build jobs in ephemeral workspaces/containers.

Required properties:

- exact-SHA checkout;
- no production database credentials;
- temporary test databases/services;
- max concurrency = 1 in initial single-VPS mode;
- resource guard before and during heavy jobs;
- deterministic evidence output;
- workspace cleanup after completion;
- artifact checksums.

### 8.5 Production Manager

Only the Production Manager may coordinate approved production mutations.

Required deployment sequence:

```text
validated exact SHA/artifact
    ↓
production preflight
    ↓
backup
    ↓
migration policy check
    ↓
create immutable release
    ↓
activate release
    ↓
restart/reload controlled services
    ↓
health + smoke + public verification
    ↓
PASS / ROLLBACK
```

### 8.6 MCP Gateway

MCP exposes semantic Control Plane tools, not unrestricted shell.

Examples:

```text
list_projects
get_project
plan_project
run_ci
get_ci_result
get_project_status
plan_deployment
deploy_release
get_logs
backup_project
rollback_project
```

High-risk operations require explicit approval policy.

Forbidden design:

```text
run_shell(command)
ssh_exec(model_generated_string)
sudo_anything(...)
```

### 8.7 Adapters

Adapters isolate external systems and host execution.

Planned adapters include:

- GitHub Adapter;
- Hostinger API Adapter;
- restricted host/VPS executor;
- Docker/systemd adapters;
- database backup/migration adapters;
- health/HTTP verification adapters.

---

## 9. Autonomous 24/7 Operating Model

The Control Plane must support unattended execution cycles.

Required runtime capabilities:

- persistent job queue;
- idempotency keys;
- per-project and per-environment locks;
- retries with bounded attempts;
- resource-aware scheduling;
- crash-safe state persistence;
- resume after process/server restart;
- watchdog/health monitoring;
- evidence for every terminal state;
- `CONTROLLED_HALT` instead of guessing.

Autonomous does not mean unrestricted. It means approved low/medium-risk workflows may proceed without repeated human confirmation when all required evidence and policies are satisfied.

---

## 10. Gate Model v11

The lifecycle remains evidence-driven, but gate authority moves into the Control Plane and FlowBiz Runner.

```text
Gate -1  Safety
Gate 0   Planning
Gate 1   FlowBiz Runner CI / Build
Gate 2   Staging or isolated rehearsal when configured
Gate 3   Production deployment / verification / rollback
Gate 4   Learning / evidence / improvements
```

### Gate 1 authoritative inputs

Gate 1 MUST consume FlowBiz Runner evidence tied to:

- repository;
- exact commit SHA;
- run ID;
- test/lint/security commands;
- result;
- timestamp;
- artifact checksum where a release artifact is produced.

GitHub Actions status is not an authoritative Gate 1 dependency in v11.

---

## 11. Release and Rollback Model

Production releases must be immutable and traceable.

Reference layout:

```text
/opt/flowbiz/clients/<project>/
├── releases/
│   ├── <release-id-a>/
│   └── <release-id-b>/
├── current -> releases/<release-id-b>/
└── shared/
```

Every promoted release must record at minimum:

- project ID;
- repository;
- exact source SHA;
- artifact checksum or deterministic source reference;
- Runner validation run ID;
- deployment run ID;
- migration state where applicable;
- health verification;
- previous release pointer;
- rollback result if rollback occurs.

---

## 12. Evidence Model v11

Evidence storage is implementation-independent but must not depend exclusively on GitHub Actions artifacts.

The Control Plane must retain references to:

- planning decisions;
- Runner logs/results;
- security outputs;
- release artifact/checksum;
- production preflight;
- backups;
- migration results;
- deployment logs;
- health/smoke results;
- rollback evidence;
- incident/post-run learning.

Evidence must remain timestamped and traceable to exact SHA and run ID.

---

## 13. Milestone Resequencing

Historical milestones PR-11 through PR-17 remain accepted history. PR-16 remains deferred pending redesign.

The v10.3 milestone order after PR-17 is **superseded**. Historical references to the old order remain audit evidence but do not control new execution order.

### PR-18 — Control Plane Orchestrator Foundation — CURRENT

Includes:

- v11 architecture baseline;
- Orchestrator deterministic state/plan contracts;
- Project Manifest contract;
- Project Registry foundation;
- Provisioner plan-only foundation;
- dependency boundaries for Runner/Production/MCP adapters;
- tests for pure deterministic behavior;
- no VPS/production mutation.

### PR-19 — FlowBiz Runner + CI Authority

- persistent CI job contract;
- ephemeral workspace/container execution;
- exact-SHA checkout;
- lint/test/security adapters;
- evidence bundle;
- single-VPS resource guard;
- concurrency = 1 baseline.

### PR-20 — Single-VPS Execution Boundary

- restricted host executor;
- service/container status adapters;
- permission boundary;
- production vs Runner filesystem isolation;
- no arbitrary model-generated shell.

### PR-21 — Immutable Release + Production Manager

- release artifact contract;
- backup/preflight;
- deployment by exact validated SHA/artifact;
- health verification;
- automatic rollback;
- deployment evidence.

### PR-22 — MCP + Approval Gateway

- semantic read/control tools;
- high-risk approval gates;
- audit identity/actor context;
- ChatGPT/Codex/Operator integration boundary;
- no general shell tool.

### PR-23 — Legacy Project Importer

- inspect/adopt existing FlowBiz projects;
- generate proposed manifest from observed state;
- owner review for material ambiguity;
- no forced rebuild of existing applications.

### PR-24 — Engineering Agent Integration

Resequences the former BA/QA/SRE/DEV milestones behind the Control Plane foundation.

- BA/QA/SRE/DEV roles;
- feature squad orchestration;
- coding-agent integration;
- GitHub branch/PR workflow;
- Runner validation dispatch.

### PR-25 — 24/7 Queue, Scheduler, Recovery

- persistent queue;
- crash recovery;
- bounded retries;
- watchdog;
- resumable jobs;
- scheduled/conditional operations.

### PR-26 — Secrets + Permission Model

- secret references, not values, in manifests;
- least-privilege identities;
- credential rotation hooks;
- protected production execution lane.

### PR-27 — Hostinger + Infrastructure Adapter

- Hostinger API integration for supported infrastructure operations;
- snapshots/backups/metrics where appropriate;
- host operations remain separated from application deploy contracts.

### PR-28 — Multi-Project Controller

- project/environment concurrency locks;
- queue fairness;
- resource-aware scheduling;
- portfolio status.

### PR-29 — Operator API / UI

- project inventory;
- job timeline;
- approvals;
- CI/release/deployment evidence;
- rollback controls.

### PR-30 — Learning + Optimization

- post-run analyzer;
- repeated-task detection;
- knowledge artifacts;
- safe workflow/prompt improvement proposals.

Further milestones are added only when required by validated dependencies.

---

## 14. PR-18 Acceptance Criteria

PR-18 is complete only when:

- [ ] v11 governing documents agree on Runner/Control Plane authority;
- [ ] no architecture statement requires GitHub Actions for CI/deploy authority;
- [ ] Project Manifest validates single-VPS mode and project identity;
- [ ] Project Registry can register/read/update projects deterministically;
- [ ] Provisioner can produce a plan without mutating the host;
- [ ] Orchestrator can create and transition a plan/run without shell access;
- [ ] project/environment locking contracts are defined or reused;
- [ ] unit tests cover deterministic core behavior;
- [ ] no production deployment, SSH, database mutation, Nginx change, firewall change, or secret value is introduced;
- [ ] transition plan for legacy GitHub Actions is documented.

---

## 15. Migration from v10.3

The migration is intentionally incremental.

### Keep

- governance principles;
- evidence model;
- GitHub adapter concepts;
- gate state machine concepts;
- repository/deployment schemas where still valid;
- audit trail;
- controlled halt behavior.

### Replace / Reframe

- GitHub Actions as execution authority → FlowBiz Runner;
- workflow YAML autorun controller → Control Plane orchestrator;
- template-only project model → manifest-driven standard/custom/advanced/legacy model;
- mock production gates → observed production evidence;
- build-on-production patterns → validated release promotion.

### Do not do during architecture migration

- do not mass-delete workflows before Runner proof;
- do not deploy the Builder to production as part of PR-18;
- do not introduce unrestricted SSH or root shell tools;
- do not move production secrets into CI;
- do not change existing client production applications.

---

## 16. Future Distributed Mode

Single-VPS is a deployment mode, not an architectural limitation.

Future migration:

```yaml
infrastructure:
  mode: distributed
```

may place Control Plane, Runner, and Production on separate hosts while keeping the same Project Manifest, Orchestrator, MCP, evidence, and deployment contracts.

No redesign should be required to make that move.

---

## Final Statement

FlowBiz AI Builder v11 is a **Single-VPS Autonomous Control Plane** designed to run continuously, safely, and deterministically.

The core rule is:

> GitHub stores source. FlowBiz Runner proves it. FlowBiz Control Plane decides and executes it. Production runs only validated releases.

If a required state, permission, artifact, health signal, or rollback path cannot be verified, the system must stop with `CONTROLLED_HALT` rather than improvise.
