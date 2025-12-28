# PR Policy — FlowBiz AI Builder

**Based on BLUEPRINT v10 Human-Inspired Engineering Model**

---

## 1. PR is Valid Only With Evidence

Every PR **MUST** contain evidence across all sections:

### Required PR Template Sections

```markdown
## Feature / Problem [BA]
- Problem statement and value
- Link to PRD/DoD if available

## Acceptance Criteria [BA]
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] ...

## Test Impact [QA]
- Tests added/updated
- Smoke/Regression coverage
- Test execution results

## Deploy / Verify Notes [SRE]
- Deployment impact
- Environment requirements
- Verify and rollback steps

## Automation & Quality [DEV]
- [ ] Tests updated
- [ ] No new manual steps
- [ ] CI passing

## Scope Lock
**In-scope:**
- Item 1
- Item 2

**Out-of-scope:**
- Item 1
- Item 2

## Knowledge Notes
- Lessons learned
- Known risks
- Future improvement notes
```

---

## 2. Gate Rules (Enforced by CI/CD)

### 🔐 Gate -1: Safety Gate
- ❌ Forbidden paths not touched (secrets, config)
- ❌ No secrets leaked
- ✅ Permissions valid

### 🔐 Gate 0: Planning Gate
- ✅ PRD / DoD documented (BA)
- ✅ Test Plan exists (QA)
- ✅ Deploy & Verify Plan (SRE)

### 🔐 Gate 1: CI Gate
- ✅ Lint passes (ruff)
- ✅ Unit tests pass (pytest)
- ✅ Security scan passes (gitleaks + pip-audit)
- ✅ Build succeeds
- ✅ Dependency & budget policy met

### 🔐 Gate 2: Staging Gate *(Future)*
- Deploy PR SHA to staging
- Smoke tests pass
- Evidence attached

### 🔐 Gate 3: Production Gate *(Future)*
- Deploy main SHA
- Verify success
- Auto rollback on failure

### 🔐 Gate 4: Learning Gate *(Future)*
- Post-run report
- Knowledge artifacts
- Suggestion PR / Issue if needed

---

## 3. PR Best Practices

### DO ✅
- **One Feature = One PR** — Keep PRs focused and small
- **Test First** — Write tests before or with your code
- **Document Impact** — Explain deployment and verification steps
- **Link Related Issues** — Reference issue numbers
- **Self-Review** — Review your own changes before requesting review
- **Update Documentation** — Keep docs in sync with code changes

### DON'T ❌
- **No Rush & Merge** — Every PR needs evidence
- **No Scope Creep** — Stick to defined scope
- **No Breaking Changes** — Without migration plan
- **No Untested Code** — All code must have tests
- **No Manual Steps** — Automate everything possible
- **No Security Risks** — Must pass security scans

---

## 4. PR Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Follow Human-Inspired Model**
   - 🔍 Discovery — Understand the problem
   - 📋 Plan — Define acceptance criteria
   - 🔨 Build — Implement with tests
   - 🚀 Release — Deploy with evidence
   - 📚 Learn — Document learnings

3. **Open PR with Template**
   - Fill all required sections
   - Link related issues
   - Request reviews from appropriate team

4. **Pass All Gates**
   - ✅ CI must be green
   - ✅ All checks must pass
   - ✅ No unresolved comments

5. **Merge**
   - Prefer **squash merge** for clean history
   - Delete branch after merge

---

## 5. Review Guidelines

### For Reviewers
- **Check Evidence** — Ensure all sections are filled
- **Verify Tests** — Run tests locally if needed
- **Check Scope** — Ensure no scope creep
- **Security Review** — Look for security issues
- **Performance** — Consider performance implications
- **Provide Constructive Feedback** — Be specific and helpful

### For Authors
- **Respond to All Comments** — Address or explain each comment
- **Update PR Description** — Keep it current with changes
- **Re-request Review** — After addressing comments
- **Be Patient** — Quality takes time

---

## 6. Special PR Types

### Hotfix PRs
- Must include `[HOTFIX]` in title
- Must explain urgency and impact
- Still requires all evidence sections
- Can skip staging gate with approval

### Documentation PRs
- Can skip build/test gates if truly doc-only
- Must update relevant docs together
- Examples, diagrams encouraged

### Dependency Update PRs
- Must explain why update is needed
- Must include security scan results
- Must verify no breaking changes

---

## 7. Enforcement

### Automated
- **CI Workflow** — Blocks merge if lint/test/security fails
- **PR Template** — Required fields enforced
- **Branch Protection** — Main branch protected

### Manual
- **Code Review** — Required approval from at least 1 reviewer
- **Policy Check** — Guardrails workflow checks for scope violations
- **Security Review** — For sensitive changes

---

## 8. Violations

### Minor Violations
- Missing optional sections → Warning comment
- Minor formatting issues → Auto-fix suggestion

### Major Violations
- Missing required sections → PR blocked
- Failed security scan → PR blocked
- No tests → PR blocked
- Scope creep detected → Review required

### Escalation
- Repeated violations → Team discussion
- Security issues → Immediate block + alert

---

## 9. References

- **BLUEPRINT.md** — Engineering model and philosophy
- **RUNBOOK.md** — Operational procedures
- **GitHub Actions** — CI/CD workflows in `.github/workflows/`

---

**Remember:** Every PR proves it followed the model. Quality over speed.
