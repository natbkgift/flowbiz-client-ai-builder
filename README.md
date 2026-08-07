# FlowBiz AI Builder

FlowBiz AI Builder is evolving into a **24/7 autonomous project and deployment control plane** for the FlowBiz portfolio.

## Current Architecture

**v11 target:** Single-VPS Autonomous Control Plane

```text
GitHub
  │  Source Authority
  ▼
FlowBiz Control Plane
  ├─ Orchestrator
  ├─ Project Registry
  ├─ Provisioner
  ├─ Policy / Approval
  ├─ MCP Gateway (planned)
  └─ Job Queue (planned)
        │
        ▼
FlowBiz Runner
  ├─ exact-SHA CI
  ├─ tests / security / build
  ├─ migration rehearsal
  └─ immutable evidence/artifacts
        │
        ▼
Production Manager (planned)
  ├─ backup
  ├─ immutable release
  ├─ migration
  ├─ health / smoke
  └─ rollback
        │
        ▼
flowbiz-vps
```

The current deployment mode keeps Control Plane, Runner, and Production on **one VPS**, separated by permission, filesystem, workload priority, and execution contracts. The contracts are designed so these lanes can move to separate hosts later without redesigning the platform.

## Authority Model

| Area | Authority |
|---|---|
| Source / branches / PRs / exact SHA | GitHub |
| CI / build / security evidence | FlowBiz Runner |
| Orchestration / policy / execution decisions | FlowBiz Control Plane |
| Active application runtime | Production VPS |

### GitHub Actions

FlowBiz AI Builder v11 **does not depend on GitHub Actions for autonomous operation**.

Existing `.github/workflows/` files are legacy transition assets. They may remain temporarily as supplemental checks, but they are non-authoritative in the target architecture and must not become the production deploy or rollback mechanism.

They will be disabled/removed only after FlowBiz Runner provides equivalent or stronger validation evidence, preventing a temporary CI gap.

## Current Milestone

### PR-18 — Control Plane Orchestrator Foundation

PR-18 establishes:

- BLUEPRINT v11;
- Project Manifest contracts;
- Project Registry foundation;
- plan-only Provisioner;
- deterministic Orchestrator state machine;
- single-VPS safety baseline;
- FlowBiz Runner / Production / MCP adapter boundaries.

PR-18 performs **no VPS, production database, Nginx, firewall, or secret mutation**.

See:
- [`BLUEPRINT.md`](BLUEPRINT.md)
- [`POLICY.md`](POLICY.md)
- [`CONTROLS.md`](CONTROLS.md)
- [`EVIDENCE.md`](EVIDENCE.md)
- [`PROJECT_STATE.md`](PROJECT_STATE.md)

## Development Baseline

Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
```

Focused v11 foundation tests:

```bash
pytest -q tests/test_control_plane_v11.py
```

## Safety Principles

- exact-SHA validation;
- immutable production releases;
- rollback required for production mutation;
- Runner jobs are ephemeral;
- initial single-VPS Runner concurrency is 1;
- Production has priority over CI workloads;
- CI has no production database credentials;
- AI tools do not receive unrestricted shell/SSH;
- unverifiable state causes `CONTROLLED_HALT`.

## Roadmap

The v10 post-PR-17 order is superseded by v11.

1. **PR-18** — Orchestrator + Registry + Provisioner foundation
2. **PR-19** — FlowBiz Runner / CI authority / resource guard
3. **PR-20** — restricted single-VPS execution boundary
4. **PR-21** — immutable release / Production Manager / rollback
5. **PR-22** — MCP + approval gateway
6. **PR-23** — legacy project importer
7. **PR-24+** — engineering agents and continuous autonomous operations

The detailed dependency graph is authoritative in [`BLUEPRINT.md`](BLUEPRINT.md).
