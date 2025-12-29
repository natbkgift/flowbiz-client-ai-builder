# Pull Request Template — FlowBiz AI Builder
## Enterprise / Audit / ISO-Ready

> **Compliance Notice**  
> This PR will be automatically blocked if mandatory sections or metadata are missing.
> All statements must be verifiable and auditable.

---

## PR Metadata (MANDATORY)

```md
PR_TYPE: MILESTONE | WIP | HOTFIX
AUTO_RUN_MODE: STRICT | GUIDED
AUTO_RUN_NEXT: NOT_READY         # Set to READY only when compliance checklist is fully met
MILESTONE_ID: PR-###            # Required for MILESTONE
BLUEPRINT_REF: Section 11 / PR-###
```

For `AUTO_RUN_MODE: GUIDED`, the following are REQUIRED:
```md
AUTHORIZATION_REASON: <why exception is required>
AUTHORIZED_BY: <human owner>
```

---

## [BA]
**Problem / Business Context**
- Business context and objective:
- User / system impact:
- Reference to PRD / DoD (link):

**Acceptance Criteria**
- [ ] Clear, testable condition #1
- [ ] Clear, testable condition #2

**Scope (Scope Lock)**
- **In Scope:**
  - 
- **Out of Scope:**
  - 

---

## [QA]
**Test Plan**
- Tests added/updated:
- Smoke tests:
- Regression coverage:
- Known gaps (if any):

---

## [SRE]
**Deployment & Verification Plan**
- Deployment impact:
- Verification checklist:
- Rollback procedure:

---

## [DEV]
**Implementation Notes**
- Summary of changes:
- Key design decisions:
- Tests updated: [Y/N]
- Docs updated (if behavior changes): [Y/N]

---

## Risk Assessment
- Risk level: Low / Medium / High
- Failure scenarios:
- Mitigation plan:

---

## Evidence & Artifacts
Link all relevant evidence:
- CI logs: https://example.com/ci-run
- Security scan results: https://example.com/security-scan
- Deployment logs: https://example.com/deploy-logs
- Screenshots / artifacts: https://example.com/artifacts

## ISO/SOC2 Impact Mapping (MANDATORY)
ISO9001_IMPACT: <Describe impact or "N/A">
ISO27001_IMPACT: <Describe impact or "N/A">
SOC2_IMPACT: <Describe impact or "N/A">

---

## Knowledge & Learning Notes
- Lessons learned:
- Follow-up actions:
- Improvement suggestions:

---

## Compliance Checklist (MANDATORY)
- [ ] PR title follows milestone naming (Control: Pull Request Policy; Evidence: Planning Evidence)
- [ ] Exactly one milestone mapped (Control: Planning Controls; Evidence: Planning Evidence)
- [ ] Blueprint section referenced (Control: Planning Controls; Evidence: Planning Evidence)
- [ ] [BA][QA][SRE][DEV] sections present (Control: Planning Controls; Evidence: Planning Evidence)
- [ ] CI required checks passed (lint/test/security) (Control: CI Controls; Evidence: CI Evidence)
- [ ] Guardrails/policy checks passed (Control: Governance Policy; Evidence: CI Evidence)
- [ ] Evidence links attached (CI logs / scan / artifacts) (Control: Evidence Requirements; Evidence: CI Evidence)
- [ ] POLICY.md reviewed (Control: Governance Policy; Evidence: Learning Evidence)
- [ ] CONTROLS.md satisfied (Control: Control Framework; Evidence: Control Effectiveness)
- [ ] EVIDENCE.md artifacts attached (Control: Evidence Requirements; Evidence: Deployment Evidence)


---

## Final Declaration

I confirm that:
- This PR complies with FlowBiz governance policies
- All claims are supported by evidence
- This change is safe to proceed under the declared mode

**Approved by (human owner):** ____________________  
**Date:** ____________________
