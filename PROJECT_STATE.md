# PROJECT_STATE

Purpose: Current external-memory snapshot for FlowBiz AI Builder v11 migration.

## Repository
- Repository: `natbkgift/flowbiz-client-ai-builder`
- Main base HEAD at PR-18 start: `80149cf2ea510168e99c513fae6705619f467aec`
- Active branch: `feature/pr-18-v11-single-vps-control-plane`
- Snapshot date: 2026-08-07

## Architecture Decision
- Target: **FlowBiz AI Builder v11 — Single-VPS Autonomous Control Plane**
- Availability target: **24/7 autonomous operation**
- Current infrastructure mode: `single-vps`
- GitHub: Source Authority
- FlowBiz Runner: CI / Build Authority
- FlowBiz Control Plane: Decision + Execution Authority
- Production VPS: Runtime Authority
- GitHub Actions: legacy/optional/non-authoritative transition path; not a target architecture dependency

## Milestones
- Historical completed functional milestone: PR-17 — Webhook Watcher & Notifications
- Deferred historical milestone: PR-16 — Policy Enforcer (requires redesign)
- **Current: PR-18 — Control Plane Orchestrator Foundation**
- Former v10 PR-19–38 order: superseded/resequenced by BLUEPRINT v11

## PR-18 Scope
- BLUEPRINT v11 architecture baseline
- governing-doc alignment for FlowBiz Runner/Control Plane authority
- Project Manifest contract
- Project Registry foundation
- Provisioner plan-only foundation
- deterministic Orchestrator state machine
- foundation tests

Explicitly out of scope for PR-18:
- VPS/SSH mutation
- production deployment
- database mutation
- Nginx/firewall changes
- real secrets
- disabling/removing legacy GitHub Actions before Runner parity proof
- unrestricted shell tools

## Validation
- Isolated PR-18 control-plane harness: PASS (Pydantic model validation + registry + provisioner + orchestrator state transition)
- Python compile check for new foundation modules: PASS
- Full repository FlowBiz Runner validation: PENDING (Runner milestone not implemented yet)
- Production operations performed by PR-18: 0

## Next Dependency
After PR-18 foundation is reviewed and validated:
1. PR-19 — FlowBiz Runner + CI Authority + single-VPS resource guard
2. PR-20 — restricted single-VPS execution boundary
3. PR-21 — immutable release / Production Manager / rollback
4. PR-22 — MCP + approval gateway
5. engineering agents follow after the Control Plane foundation

## Owner Authorization
See `AUTORUN_DECISIONS.md` entry dated 2026-08-07.
