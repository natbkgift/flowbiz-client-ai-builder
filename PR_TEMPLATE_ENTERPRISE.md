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
MILESTONE_ID: PR-###            # Required for MILESTONE
BLUEPRINT_REF: Section 11 / PR-###
```

For `AUTO_RUN_MODE: GUIDED`, the following are REQUIRED:
```md
AUTHORIZATION_REASON: <why exception is required>
AUTHORIZED_BY: <human owner>
```

---

## 1. Feature / Problem Statement (BA)
- Business context and objective
- User / system impact
- Reference to PRD / DoD (link)

---

## 2. Acceptance Criteria (BA)
- [ ] Clear, testable condition #1
- [ ] Clear, testable condition #2

---

## 3. Test Impact & Coverage (QA)
- Tests added/updated:
- Smoke tests:
- Regression coverage:
- Known gaps (if any):

---

## 4. Deployment & Verification Plan (SRE)
- Deployment impact:
- Verification checklist:
- Rollback procedure:

---

## 5. Automation & Quality Assurance
- [ ] Tests updated or added
- [ ] No new manual operational steps
- [ ] Idempotent behavior verified

---

## 6. Scope Control (Scope Lock)
**In Scope**
- 

**Out of Scope**
- 

---

## 7. Risk Assessment
- Risk level: Low / Medium / High
- Failure scenarios:
- Mitigation plan:

---

## 8. Evidence & Artifacts
Link all relevant evidence:
- CI logs:
- Security scan results:
- Deployment logs:
- Screenshots / artifacts:

---

## 9. Knowledge & Learning Notes
- Lessons learned:
- Follow-up actions:
- Improvement suggestions:

---

## 10. Compliance Checklist (MANDATORY)
- [ ] PR title follows `PR-###: <milestone name>`
- [ ] Exactly one milestone mapped
- [ ] Blueprint section referenced
- [ ] POLICY.md reviewed
- [ ] CONTROLS.md satisfied
- [ ] EVIDENCE.md artifacts attached

---

## Final Declaration

I confirm that:
- This PR complies with FlowBiz governance policies
- All claims are supported by evidence
- This change is safe to proceed under the declared mode

**Approved by (human owner):** ____________________
**Date:** ____________________
