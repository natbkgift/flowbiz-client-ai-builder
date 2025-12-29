# 🛡️ SOC 2 AUDIT PACK — FlowBiz AI Builder
## Trust Services Criteria (TSC) — Audit-Ready Documentation

This document demonstrates how **FlowBiz AI Builder** complies with
**SOC 2 Trust Services Criteria** through documented governance, controls,
and verifiable evidence.

---

## 1. Audit Scope

**System:** FlowBiz AI Builder (AI-driven CI/CD & Engineering Orchestration Platform)  
**In Scope:**
- Source code management (GitHub)
- CI/CD pipelines
- AI-assisted PR creation and review
- Deployment automation
- Evidence and audit logging

**Out of Scope:**
- End-user data processing
- Customer application runtime (unless explicitly onboarded)

---

## 2. Governing Documents

The following documents are authoritative for SOC 2 compliance:

- `POLICY.md` — Governance & Engineering Policy
- `CONTROLS.md` — Control Framework & Gates
- `EVIDENCE.md` — Evidence & Audit Artifacts
- `BLUEPRINT.md` — Engineering Roadmap & Milestones
- `.github/pull_request_template.md`
- `CODEX_AUTORUN_PROMPT_v1.1.md`

Order of precedence:
**POLICY → CONTROLS → BLUEPRINT → PROMPT → WORKFLOWS**

---

## 3. Trust Services Criteria Coverage

### CC1 — Control Environment
| SOC 2 Ref | Control Description | Implementation | Evidence |
|---|---|---|---|
| CC1.1 | Integrity & ethical values | Mandatory PR governance | POLICY — Core Policy Principles |
| CC1.2 | Accountability | Feature Squad model | BLUEPRINT — Feature Squad Accountability |
| CC1.3 | Oversight | Human approval gates | CONTROLS — Planning Controls (Gate 0) |
| CC1.4 | Competence | Role-based agents | BLUEPRINT — Feature Squad Accountability |
| CC1.5 | Responsibility | Named authorization | PR metadata |

---

### CC2 — Communication & Information
| SOC 2 Ref | Description | Implementation | Evidence |
|---|---|---|---|
| CC2.1 | Internal communication | PR templates & comments | PR history |
| CC2.2 | Policy dissemination | Repo governance docs | POLICY.md |
| CC2.3 | Change communication | CI status & notifications | CI logs |
| CC2.4 | External comms | Webhook notifications | CONTROLS — CI Controls |

---

### CC3 — Risk Assessment
| SOC 2 Ref | Description | Implementation | Evidence |
|---|---|---|---|
| CC3.1 | Risk identification | Planning Gate | Gate 0 artifacts |
| CC3.2 | Fraud risk | Scope lock + approvals | PR checks |
| CC3.3 | Change risk | One PR = one milestone | [BLUEPRINT — Milestone Traceability](BLUEPRINT.md#4-milestone-traceability) |
| CC3.4 | Risk mitigation | CI + rollback | CI / deploy logs |

---

### CC4 — Monitoring Activities
| SOC 2 Ref | Description | Implementation | Evidence |
|---|---|---|---|
| CC4.1 | Ongoing monitoring | CI status checks | GitHub Actions |
| CC4.2 | Deficiency eval | FAIL_SAFE triggers | Incident PRs |
| CC4.3 | Corrective action | HOTFIX workflow | HOTFIX PRs |
| CC4.4 | Control validation | Auto Review Agent | PR comments |

---

### CC5 — Control Activities
| SOC 2 Ref | Description | Implementation | Evidence |
|---|---|---|---|
| CC5.1 | Change authorization | PR approval rules | Branch rules |
| CC5.2 | Segregation of duties | Agent role separation | [BLUEPRINT — Feature Squad Accountability](BLUEPRINT.md#7-feature-squad-accountability) |
| CC5.3 | Change validation | CI + staging | Test results |
| CC5.4 | Secure deployment | Controlled release | Deploy logs |

---

## 4. Security Criteria

### CC6 — Logical & Physical Access
| SOC 2 Ref | Description | Implementation | Evidence |
|---|---|---|---|
| CC6.1 | Access control | GitHub permissions | Repo settings |
| CC6.2 | Least privilege | Fine-grained tokens | POLICY — Approval & Authority |
| CC6.3 | Credential protection | Secrets mgmt | GitHub secrets |
| CC6.4 | Access revocation | Repo access logs | Audit logs |

---

### CC7 — System Operations
| SOC 2 Ref | Description | Implementation | Evidence |
|---|---|---|---|
| CC7.1 | Ops procedures | CI/CD workflows | Workflows |
| CC7.2 | Monitoring | CI + alerts | Logs |
| CC7.3 | Incident response | FAIL_SAFE + HOTFIX | Incident PR |
| CC7.4 | Root cause analysis | Post-run analyzer | Reports |

---

### CC8 — Change Management
| SOC 2 Ref | Description | Implementation | Evidence |
|---|---|---|---|
| CC8.1 | Change approval | PR workflow | PR history |
| CC8.2 | Change testing | CI / Staging Gate | Test logs |
| CC8.3 | Change deployment | Production Gate | Deploy evidence |
| CC8.4 | Rollback | Auto rollback | Rollback logs |

---

### CC9 — Risk Mitigation
| SOC 2 Ref | Description | Implementation | Evidence |
|---|---|---|---|
| CC9.1 | Vendor risk | Template guardrails | Blueprint |
| CC9.2 | Dependency risk | Dependency scan | Scan reports |
| CC9.3 | Incident learning | Learning Gate | Lessons docs |

---

## 5. Auditor Guidance

Auditors can verify compliance by:
1. Sampling merged PRs
2. Checking PR template completion
3. Reviewing CI / security logs
4. Tracing evidence links per PR
5. Confirming rollback capability

---

## 6. Management Assertion

Management asserts that:
- Controls are designed effectively
- Controls operate as described
- Evidence is retained and auditable

This audit pack supports **SOC 2 Type I** readiness and can be extended
to **SOC 2 Type II** with operational history.

---

## Appendix — Evidence Index (Example)

| Artifact | Location |
|---|---|
| PR templates | `.github/pull_request_template.md` |
| CI logs | GitHub Actions |
| Security scans | CI artifacts |
| Deployment logs | EVIDENCE.md references |
