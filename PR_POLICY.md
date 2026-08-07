# PR Policy — FlowBiz AI Builder v11

**Architecture:** Single-VPS Autonomous Control Plane  
**CI authority:** FlowBiz Runner  
**Source authority:** GitHub

---

## 1. PR Validity

Every material PR MUST include auditable evidence for:
- problem/context and acceptance criteria `[BA]`;
- test/regression plan `[QA]`;
- deploy/verify/rollback impact `[SRE]`;
- implementation notes `[DEV]`;
- scope lock;
- risk assessment;
- evidence references;
- learning/follow-up notes.

One PR maps to one approved milestone/scope lock.

---

## 2. Gate Rules

### Gate -1 — Safety
- forbidden/sensitive paths checked;
- secrets not leaked;
- permissions valid;
- no arbitrary production shell path introduced.

### Gate 0 — Planning
- intent/PRD/DoD documented;
- acceptance criteria defined;
- test plan exists;
- deploy/verify/rollback plan exists where applicable.

### Gate 1 — FlowBiz Runner CI
Authoritative evidence is produced by FlowBiz Runner against an exact commit SHA.

Where applicable:
- lint;
- unit/integration tests;
- security/dependency scan;
- build;
- migration rehearsal;
- E2E/browser tests;
- artifact checksum.

Legacy GitHub Actions may run during migration but are supplemental/non-authoritative and MUST NOT be the sole condition for a v11 merge/deploy decision.

### Gate 2 — Staging / Isolated Rehearsal
- staging exact SHA when staging exists, or approved isolated rehearsal;
- smoke/regression evidence;
- no production credentials in Runner test environments.

### Gate 3 — Production
- deploy only validated exact main SHA or immutable artifact;
- backup/rollback readiness before risky mutation;
- controlled migration;
- health/smoke/public verification;
- automatic rollback or `CONTROLLED_HALT` on failure.

### Gate 4 — Learning
- post-run report;
- evidence finalization;
- lessons/improvement proposal where applicable.

---

## 3. Source Change Rules

### DO
- use branches and PRs;
- identify exact SHA;
- keep changes scoped;
- use FlowBiz Runner evidence;
- keep production releases immutable;
- make rollback deterministic.

### DO NOT
- push normal feature work directly to `main`;
- edit active production release files as the normal customization path;
- expose unrestricted shell/SSH tools to AI;
- use production DB credentials in Runner jobs;
- rely on GitHub Actions availability for autonomous operation;
- merge/deploy when required evidence is missing.

---

## 4. Workflow

```text
Branch / PR
    ↓
Exact SHA
    ↓
FlowBiz Runner
    ↓
CI Evidence
    ↓
Review / Policy Decision
    ↓
Merge
    ↓
Exact main SHA release validation
    ↓
Control Plane Production Gate
```

Documentation-only changes may use a reduced Runner gate when the Control Plane classifies them as no-runtime-impact, but planning/evidence requirements still apply.

---

## 5. Merge Policy

Merge method follows active owner authorization and repository rules.

A PR MUST NOT be treated as ready when:
- required FlowBiz Runner evidence is missing/failed;
- scope lock is violated;
- required approval is absent;
- material review threads remain unresolved;
- exact SHA changed after validation without a new validation run;
- production plan lacks rollback for a risky mutation.

---

## 6. GitHub Actions Transition

Existing `.github/workflows/` files are legacy transition assets until FlowBiz Runner parity is proven.

They may remain enabled temporarily for visibility or supplemental checks, but:
- no new production deployment dependency may be added to them;
- no v11 component may require them as its only execution path;
- their outage/quota/approval state must not stop the future 24/7 Control Plane once Runner evidence is active.

Workflow removal/disablement is a later controlled change after Runner parity evidence exists.

---

## 7. Enforcement

Authoritative enforcement belongs to FlowBiz Control Plane + Runner contracts.

GitHub branch protection and workflow checks may provide defense in depth, but named GitHub Actions jobs are not the architectural source of control effectiveness in v11.

Violations produce `CONTROLLED_HALT` with a documented reason and preserved state.

---

## 8. References

- `POLICY.md`
- `CONTROLS.md`
- `BLUEPRINT.md`
- `EVIDENCE.md`
- `COMPLIANCE_CHECKLIST.md`

**Rule:** GitHub stores source; FlowBiz Runner proves it; FlowBiz Control Plane decides and executes it.
