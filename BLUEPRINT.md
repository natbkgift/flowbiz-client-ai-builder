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
- PR title MUST be: PR ###: <milestone name>
- PR body MUST include:
- MILESTONE_ID: PR ###
- BLUEPRINT_REF: Section 11 / PR ### (this list)

### Milestone Checklist
PR #11 — Foundation + Human Model + PR Policy (Template)

เป้าหมาย: วาง “กฎหมายสูงสุด” ของระบบ
Agent ต้องทำ:

สร้างโครง repo ขั้นต่ำ (folders, docs)

ใส่ BLUEPRINT.md (Human-Inspired Engineering Model)

ใส่ PR_POLICY.md + PR template

สร้าง health endpoints (/healthz, /readyz, /version)

ทำให้รันได้ local (docker compose basic หรือ uvicorn)

ห้ามทำ: business logic, agent, deploy
Done เมื่อ: เปิด PR ได้ + CI ยังไม่ต้องครบ

PR #12 — CI Baseline + Security Scan (ขั้นต่ำ)

เป้าหมาย: ทุก PR ต้อง “ไม่พังเงียบ”
Agent ต้องทำ:

GitHub Actions: lint + test + build

เพิ่ม security scan ขั้นต่ำ (gitleaks / pip-audit)

cache + cancel-in-progress

update RUNBOOK: ถ้า CI fail ทำยังไง

Done เมื่อ: push แล้ว CI เขียว

PR #13 — GitHub Adapter v1 (เปิด PR ได้จริง)

เป้าหมาย: ระบบสร้าง PR ได้เอง
Agent ต้องทำ:

เชื่อม GitHub API (create branch, commit, PR)

update PR body อัตโนมัติ (ตาม template)

อ่าน PR status / checks

ห้ามทำ: webhook / policy enforcement
Done เมื่อ: สร้าง PR จริงใน repo ทดสอบได้

PR #14 — Gate Framework v1 (Planning/CI/Staging/Prod/Learning)

เป้าหมาย: รวม “ด่านทั้งหมด” เป็น framework เดียว
Agent ต้องทำ:

นิยาม Gate: Planning, CI, Staging, Prod, Learning

state machine ของ run

แต่ละ gate = pass / fail / block

ห้ามทำ: deploy จริง
Done เมื่อ: run หนึ่งตัวเดินผ่าน gate แบบ mock ได้ครบ

PR #15 — Evidence Model + Artifact Registry v1

เป้าหมาย: ทุกการตัดสินใจต้องมีหลักฐาน
Agent ต้องทำ:

model สำหรับ evidence (PR, CI, deploy, verify)

artifact registry (file/link-based)

ผูก evidence กับ run id

Done เมื่อ: ดู run แล้วรู้ว่า “ทำอะไรไปบ้าง”

PR #16 — Policy Enforcer (PR policy + forbidden paths + deps)

เป้าหมาย: บังคับกติกาจริง
Agent ต้องทำ:

ตรวจ PR template ครบไหม

block forbidden paths

ตรวจ dependency changes

comment/label/block PR อัตโนมัติ

Done เมื่อ: PR ที่ผิด policy ถูก block จริง

PR #17 — Webhook Watcher + Notifications v1

เป้าหมาย: ระบบรู้สถานะโดยไม่ต้อง poll
Agent ต้องทำ:

รับ GitHub webhook (PR, check_run)

update run status

notify 1 ช่องทางก่อน (เช่น Discord)

Done เมื่อ: CI fail/green มีแจ้งเตือน

PR #18 — Orchestrator (Squad Lead)

เป้าหมาย: สมองคุมลำดับงาน
Agent ต้องทำ:

สร้าง Orchestrator service

เรียก BA/QA/SRE/Dev ตามลำดับ

ผูก orchestrator กับ gate framework

Done เมื่อ: 1 feature run ถูกควบคุมจากจุดเดียว

PR #19 — BA Agent (PRD/DoD generator)

เป้าหมาย: แปลง idea → PRD
Agent ต้องทำ:

รับ problem/idea

สร้าง PRD + Acceptance Criteria

output เป็นไฟล์/section ที่ gate อ่านได้

Done เมื่อ: Planning Gate ใช้ BA output ได้จริง

PR #20 — QA Agent (test plan + smoke)

เป้าหมาย: คุณภาพตั้งแต่ต้น
Agent ต้องทำ:

สร้าง test plan

ระบุ smoke / regression

map test กับ acceptance criteria

Done เมื่อ: CI/Staging gate อ่าน test plan ได้

PR #21 — SRE Agent (deploy/verify/rollback plan)

เป้าหมาย: ส่งของอย่างรับผิดชอบ
Agent ต้องทำ:

สร้าง deploy plan

verify checklist

rollback plan (ชัดเจน)

Done เมื่อ: Prod Gate ใช้ plan นี้ตัดสินใจได้

PR #22 — Dev Agent (Codex prompt consumer)

เป้าหมาย: เขียนโค้ดตาม spec
Agent ต้องทำ:

รับ refined prompt

สร้าง commit/PR

ไม่ข้าม policy/gate

Done เมื่อ: PR ที่เปิดผ่าน policy ขั้นต้น

PR #23 — Codex Prompt Engine (draft→refine→final)

เป้าหมาย: ลด PR หลุด scope
Agent ต้องทำ:

load prompt template

refine (critic ลด scope)

generate final Codex prompt

Done เมื่อ: prompt มี acceptance + test hint

PR #24 — Auto Review v1 (risk + policy checks + summary)

เป้าหมาย: รีวิวอัตโนมัติแบบมีสมอง
Agent ต้องทำ:

diff summary

risk analysis

policy violation summary

comment ลง PR

Done เมื่อ: reviewer เห็นภาพใน 1 comment

PR #25 — Docker Compose + systemd (builder)

เป้าหมาย: รัน production ได้จริง
Agent ต้องทำ:

docker-compose.yml

systemd service (auto-start/restart)

env separation

Done เมื่อ: reboot VPS แล้วยังรันอยู่

PR #26 — CD Staging Automation (deploy PR SHA → verify)

เป้าหมาย: feedback เร็วก่อน merge
Agent ต้องทำ:

deploy PR SHA ไป staging

run smoke

เก็บ evidence

Done เมื่อ: Staging Gate ทำงานอัตโนมัติ

PR #27 — CD Production + Rollback (deploy main → verify → rollback)

เป้าหมาย: production safety
Agent ต้องทำ:

deploy main SHA

verify

rollback auto เมื่อ fail

Done เมื่อ: fail test → rollback ได้จริง

PR #28 — Feature Flags / Kill Switch (runtime override)

เป้าหมาย: แก้ปัญหาโดยไม่ redeploy
Agent ต้องทำ:

feature flag config

runtime override

audit override

Done เมื่อ: ปิด feature ได้ทันที

PR #29 — Concurrency Locks + Idempotency

เป้าหมาย: กันงานชน / ซ้ำ
Agent ต้องทำ:

per-project lock

per-env lock

idempotent run handling

Done เมื่อ: deploy ซ้อนกันไม่ได้

PR #30 — Project Registry (multi-repo)

เป้าหมาย: ดูแลหลาย repo
Agent ต้องทำ:

register project

config per repo

map repo → pipeline

Done เมื่อ: เลือก repo แล้ว run ได้

PR #1 — Repo Readiness Checker (score + gaps)

เป้าหมาย: ไม่ดึง repo ที่ยังไม่พร้อม
Agent ต้องทำ:

ตรวจ CI, structure, secrets

ให้ readiness score

แนะนำสิ่งที่ขาด

Done เมื่อ: รู้ว่า repo พร้อม production ไหม

PR #32 — Onboarding PR Generator (golden templates)

เป้าหมาย: ยกระดับ repo อัตโนมัติ
Agent ต้องทำ:

generate PR เติมมาตรฐาน

ใช้ golden templates ตาม stack

Done เมื่อ: repo ใหม่ถูกยกระดับด้วย PR เดียว

PR #33 — Multi-project deploy controller (per-project configs)

เป้าหมาย: deploy หลายโปรเจคพร้อมกัน
Agent ต้องทำ:

config แยก per project

route deploy ตาม config

respect locks

Done เมื่อ: builder คุมหลาย project ได้

PR #34 — Post-run Analyzer (root cause + lessons)

เป้าหมาย: เรียนรู้จากทุก run
Agent ต้องทำ:

วิเคราะห์ fail/success

สรุป root cause

generate lessons

Done เมื่อ: มี report หลัง run ทุกครั้ง

PR #35 — Knowledge Sharing System (auto artifacts pack)

เป้าหมาย: ความรู้ไม่หาย
Agent ต้องทำ:

สร้าง artifact pack อัตโนมัติ

link กับ run/PR

Done เมื่อ: เปิด run เก่าแล้วเข้าใจทันที

PR #36 — Prompt/Workflow Tuning (safe scope)

เป้าหมาย: AI เก่งขึ้นแบบไม่อันตราย
Agent ต้องทำ:

ปรับ prompt/workflow จาก feedback

จำกัด scope (no behavior drift)

Done เมื่อ: คุณภาพดีขึ้นโดยไม่พังของเก่า

PR #37 — Secrets & Permissions Model (least-privilege)

เป้าหมาย: security ระดับ production
Agent ต้องทำ:

GitHub App / fine-grained token

deploy key แยก env

permission matrix

Done เมื่อ: secret หลุดยากมาก

PR #38 — Core Adapter Boundary (mock→core switch + contract tests)

เป้าหมาย: เชื่อม core อย่างปลอดภัย
Agent ต้องทำ:

adapter interface

mock/core switch

contract compatibility tests

Done เมื่อ: เปลี่ยน core ได้โดยไม่รื้อ builder

---

## Final Note

This blueprint encodes **how a mature engineering organization works** into an AI-driven system.

It is not just a tool —  
it is an **AI Engineering Organization as a Platform**.
