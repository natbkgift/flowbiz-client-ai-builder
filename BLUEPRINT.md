# 🧠 BLUEPRINT v10 — flowbiz-ai-builder

**Human-Inspired, Policy-Driven AI Engineering Platform (MVP → Scale)**  
Multi-Agent • Multi-Repo • CI/CD/Prod • Audit-Ready • Self-Improving

> Every PR proves it followed the model.

---

## 1) Core Philosophy

**Human-Inspired Engineering Model = Supreme Law**

Every PR, Workflow, and Deployment must provide **evidence** that it followed:

**Discovery → Plan → Build → Release → Learn**

Principles:
- ❌ No “rush & merge”
- ✅ Evidence-driven delivery
- ✅ MVP-first, then harden
- ✅ Automation over repetition

---

## 2) PR Policy (Mandatory)

A PR is considered **valid** only if it contains evidence across **all sections below**.

### PR Template (Required)

```md
## Feature / Problem (BA)
Problem statement and value (link PRD/DoD)

## Acceptance Criteria (BA)
- [ ] ...

## Test Impact (QA)
- Tests added/updated
- Smoke/Regression coverage

## Deploy / Verify Notes (SRE)
- Deployment impact
- Verify and rollback steps

## Automation & Quality
- [ ] Tests updated
- [ ] No new manual steps

## Scope Lock
In-scope / Out-of-scope

## Knowledge Notes
Lessons learned / risks / future notes
```

---

## 3) Gate Rules (Enforced)

### 🔐 Gate -1: Safety Gate
- Forbidden paths not touched
- Secrets not leaked
- Permissions valid

### 🔐 Gate 0: Planning Gate
- PRD / DoD (BA)
- Test Plan (QA)
- Deploy & Verify Plan (SRE)

### 🔐 Gate 1: CI Gate
- Lint
- Unit tests
- Security scan
- Dependency & budget policy

### 🔐 Gate 2: Staging Gate
- Deploy PR SHA to staging
- Smoke tests pass
- Evidence attached

### 🔐 Gate 3: Production Gate
- Deploy main SHA
- Verify success
- Auto rollback on failure

### 🔐 Gate 4: Learning Gate
- Post-run report
- Knowledge artifacts
- Suggestion PR / Issue if needed

---

## 4) Feature Squad Model

**1 Feature = 1 Temporary Squad**

Squad members:
- BA Agent
- QA Agent
- SRE Agent
- Dev Agent (code author – only one)
- UX / Data Agent (optional)

Rules:
- No Squad → No PR
- 1 PR = 1 Dev Agent
- Orchestrator = Squad Lead

---

## 5) Automation First Rule

> Any task repeated more than **3 times** must be automated.

The system will block PRs that introduce unnecessary manual steps.

---

## 6) Knowledge Sharing = System

Each feature automatically produces:

- `feature-summary.md`
- `lessons-learned.md`
- `test-gaps.md`
- `deploy-notes.md`

These replace manual sharing sessions and are fully auditable.

---

## 7) Multi-Repo & Onboarding

Flow:
1. Link GitHub repository
2. Run readiness check
3. If missing standards → generate onboarding PR
4. If ready → enter CI / Staging / Production pipeline

Golden templates provided per stack:
- FastAPI
- Node.js
- Worker / Cron

---

## 8) Production Essentials

### Concurrency & Safety
- Per-project lock
- Per-environment lock (staging / prod)
- Idempotent runs

### Secrets & Permissions
- Least-privilege GitHub App
- Separate deploy keys per environment
- Environment approvals

### Release & Versioning
- Semantic tags
- Auto changelog
- Current version tracked per environment

---

## 9) Core Integration Strategy

`flowbiz-ai-builder` operates **independently first**.

Integration with `flowbiz-ai-core`:
- Contract-first
- Adapter-based
- Mock → Core switch
- No hard dependency

---

## 10) Success Metrics

- Time to open PR < 5 minutes
- CI failure rate decreasing
- Deploy success rate > 95%
- Rollback time < 2 minutes
- Budget within limits

---

## 11) PR Index (Milestones / Source of Truth)

Rule:
- 1 PR = 1 milestone (scope lock)
- PR title MUST be: PR##: <milestone name>
- PR body MUST include:
- MILESTONE_ID: PR##
- BLUEPRINT_REF: Section 11 / PR## (this list)

### Milestone Checklist
PR9 — Foundation + Human Model + PR Policy (Template)
PR10 — CI Baseline + Security Scan (ขั้นต่ำ)
PR11 — GitHub Adapter v1 (เปิด PR ได้จริง)
PR12 — Gate Framework v1 (Planning/CI/Staging/Prod/Learning)
PR13 — Evidence Model + Artifact Registry v1
PR14 — Policy Enforcer (PR policy + forbidden paths + deps)
PR15 — Webhook Watcher + Notifications v1
PR16 — Orchestrator (Squad Lead)
PR17 — BA Agent (PRD/DoD generator)
PR18 — QA Agent (test plan + smoke)
PR19 — SRE Agent (deploy/verify/rollback plan)
PR20 — Dev Agent (Codex prompt consumer)
PR21 — Codex Prompt Engine (draft→refine→final)
PR22 — Auto Review v1 (risk + policy checks + summary)
PR23 — Docker Compose + systemd (builder)
PR24 — CD Staging Automation (deploy PR SHA → verify)
PR25 — CD Production + Rollback (deploy main → verify → rollback)
PR26 — Feature Flags / Kill Switch (runtime override)
PR27 — Concurrency Locks + Idempotency
PR28 — Project Registry (multi-repo)
PR29 — Repo Readiness Checker (score + gaps)
PR30 — Onboarding PR Generator (golden templates)
PR31 — Multi-project deploy controller (per-project configs)
PR32 — Post-run Analyzer (root cause + lessons)
PR33 — Knowledge Sharing System (auto artifacts pack)
PR34 — Prompt/Workflow Tuning (safe scope)
PR35 — Secrets & Permissions Model (least-privilege)
PR36 — Core Adapter Boundary (mock→core switch + contract tests)

---

## Final Note

This blueprint encodes **how a mature engineering organization works** into an AI-driven system.

It is not just a tool —  
it is an **AI Engineering Organization as a Platform**.
