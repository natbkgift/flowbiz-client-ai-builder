## [BA]
<!-- Business Analyst perspective: Problem statement and acceptance criteria -->

**Feature / Problem:**
<!-- Describe the problem being solved and the value it provides -->

**Acceptance Criteria:**
- [ ] ...
- [ ] ...

**Scope:**
- **In-scope:** ...
- **Out-of-scope:** ...

---

## [QA]
<!-- Quality Assurance perspective: Testing and coverage -->

**Test Plan:**
<!-- Describe how this was tested -->
- [ ] Tested locally with `docker compose up`
- [ ] All tests pass (`pytest -q`)
- [ ] Linting passes (`ruff check .`)

**Test Impact:**
- Tests added/updated: ...
- Smoke/Regression coverage: ...

---

## [SRE]
<!-- Site Reliability Engineering perspective: Deployment and operations -->

**Deploy Impact:**
<!-- What changes in deployment, infrastructure, or operations? -->

**Verification Steps:**
<!-- How to verify this works in production -->
1. ...
2. ...

**Rollback Plan:**
<!-- How to rollback if issues arise -->

---

## [DEV]
<!-- Developer perspective: Implementation details -->

**Implementation Notes:**
<!-- Key technical decisions and approach -->

**Tests Added/Updated:**
<!-- List test files changed -->

**Documentation Updated:**
<!-- List docs changed, or state "N/A" -->

---

## Automation & Quality
- [ ] Tests updated
- [ ] No new manual steps introduced
- [ ] No security vulnerabilities introduced

## Pre-flight
<!-- Reference docs/CODEX_PREFLIGHT.md for complete checklist -->
- [ ] API contracts maintained
- [ ] Environment conventions followed
- [ ] No scope creep
- [ ] Appropriate persona labels added (persona:core|infra|docs)
