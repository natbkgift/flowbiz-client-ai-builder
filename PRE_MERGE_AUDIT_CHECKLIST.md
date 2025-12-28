# ✅ PRE-MERGE AUDIT CHECKLIST
## FlowBiz AI Builder — SOC2 / ISO 9001 / ISO 27001

> **Purpose**  
> This checklist MUST be completed before any PR is merged.
> It provides auditable proof that governance, quality, and security controls
> were executed as designed.

---

## 🔐 A. Governance & Metadata (MANDATORY)

- [ ] PR title follows format: `PR-###: <milestone name>`
- [ ] `PR_TYPE` declared (MILESTONE / WIP / HOTFIX)
- [ ] `AUTO_RUN_MODE` declared (STRICT / GUIDED)
- [ ] `MILESTONE_ID` present and matches PR title
- [ ] `BLUEPRINT_REF` present and correct
- [ ] PR maps to **exactly one milestone**
- [ ] No scope creep detected

**If any item fails → MERGE MUST BE BLOCKED**

---

## 🧠 B. Blueprint & Policy Compliance

- [ ] PR scope matches milestone definition in `BLUEPRINT.md`
- [ ] Changes comply with `POLICY.md`
- [ ] Required controls in `CONTROLS.md` are satisfied
- [ ] No forbidden paths or actions introduced
- [ ] Any exception is documented and authorized

---

## 🧪 C. Quality Assurance (QA)

- [ ] Acceptance criteria are clear and testable
- [ ] Tests added or updated where required
- [ ] Regression impact assessed
- [ ] CI results reviewed and acceptable
- [ ] No failing or missing required checks

---

## 🚀 D. Deployment & Reliability (SRE)

- [ ] Deployment impact documented
- [ ] Verification steps defined and reasonable
- [ ] Rollback plan documented and feasible
- [ ] No irreversible production changes

---

## 🔒 E. Security & Risk

- [ ] Security scans executed (static / dependency)
- [ ] No HIGH / CRITICAL vulnerabilities unresolved
- [ ] Secrets handled via approved mechanisms
- [ ] Access changes reviewed (if applicable)

---

## 📂 F. Evidence & Audit Trail

- [ ] Evidence links provided (CI logs, scans, artifacts)
- [ ] Evidence is traceable to PR and milestone
- [ ] Evidence complies with `EVIDENCE.md`
- [ ] No evidence gaps identified

---

## 📘 G. Learning & Improvement

- [ ] Lessons learned documented (if applicable)
- [ ] Follow-up actions recorded or ticketed
- [ ] Improvement opportunities noted

---

## 🧾 H. ISO / SOC2 Mapping Confirmation

- [ ] ISO 9001 clauses impacted are identified
- [ ] ISO/IEC 27001 Annex A controls considered
- [ ] SOC 2 Trust Services Criteria covered
- [ ] No unmanaged compliance gaps

---

## ✍️ Reviewer Declaration (MANDATORY)

I confirm that:
- This PR complies with FlowBiz governance, quality, and security controls
- All checklist items have been verified
- Evidence is sufficient for audit purposes

**Reviewer Name:** __________________________
**Role:** __________________________  
**Date:** __________________________  

---

## 🔴 Enforcement Rule

If this checklist is incomplete or inaccurate:
- PR MUST NOT be merged
- Status = `CONTROLLED_HALT`
- Reason must be documented in PR comment
