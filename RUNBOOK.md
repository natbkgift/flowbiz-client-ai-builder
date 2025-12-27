# RUNBOOK — FlowBiz Client AI Builder

## CI Failure Response Procedures

### Quick Reference

**Status Page:** https://github.com/natbkgift/flowbiz-client-ai-builder/actions

**Primary Contact:** Repository maintainers via GitHub issues

---

## 1. CI Workflow Failures

### Symptoms
- GitHub Actions "CI" workflow shows red ❌ status
- PR cannot be merged
- Main branch shows failing checks

### Response Steps

#### Step 1: Identify the Failing Job
```bash
# Navigate to Actions tab in GitHub
# Click on the failing workflow run
# Identify which job failed: lint, test, security-scan, or build
```

#### Step 2: Lint Failures
```bash
# Clone the repository
git clone https://github.com/natbkgift/flowbiz-client-ai-builder
cd flowbiz-client-ai-builder

# Run linter locally
ruff check .
ruff format --check .

# Auto-fix issues
ruff check --fix .
ruff format .

# Commit fixes
git add .
git commit -m "fix: lint errors"
git push
```

#### Step 3: Test Failures
```bash
# Run tests locally
pytest -v

# Run specific test file
pytest tests/test_health.py -v

# Run with more verbosity
pytest -vv --tb=long

# Fix failing tests
# Edit test files or source code
# Re-run tests until green
git add .
git commit -m "fix: failing tests"
git push
```

#### Step 4: Security Scan Failures

**Gitleaks (Secret Detection)**
```bash
# If gitleaks finds secrets:
# 1. NEVER commit the secret
# 2. Rotate the exposed secret immediately
# 3. Remove from git history:
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch PATH/TO/FILE' \
  --prune-empty --tag-name-filter cat -- --all

# 4. Force push (ONLY if not on main)
git push origin --force --all
```

**pip-audit (Dependency Vulnerabilities)**
```bash
# Run locally
pip install pip-audit
pip-audit --desc

# Fix vulnerabilities
# Update affected package in pyproject.toml
pip install -e ".[dev]"

# Re-test
pip-audit --desc
pytest -v
```

#### Step 5: Build Failures
```bash
# Test Python package build
pip install build
python -m build

# Test Docker build
docker build -t flowbiz-client-ai-builder:test .
docker run --rm flowbiz-client-ai-builder:test python -c "import apps.api.main"

# Common issues:
# - Missing dependencies → update pyproject.toml
# - Import errors → check package structure
# - Dockerfile issues → verify Dockerfile syntax
```

---

## 2. Policy Check Failures

### Symptoms
- "Policy Check" workflow fails
- PR body missing required sections
- Forbidden paths modified

### Response Steps

```bash
# Ensure PR includes ALL required sections:
# [BA] - Business Analyst section
# [QA] - Quality Assurance section  
# [SRE] - Site Reliability Engineering section
# [DEV] - Development section

# Edit PR description to add missing sections
# Use template from .github/pull_request_template.md
```

---

## 3. Main Branch Failures (FAIL_SAFE)

### Symptoms
- Main branch CI shows red ❌
- Production deployment blocked
- AUTO_RUN controller stops

### Response Steps (URGENT)

**FAIL_SAFE_HOTFIX_TRIGGERED**

1. **Stop all feature work immediately**
2. **Create hotfix branch**
```bash
git checkout main
git pull origin main
git checkout -b hotfix/restore-main-green
```

3. **Identify root cause**
```bash
# Check recent commits
git log --oneline -10

# Check CI logs for main branch
# Visit: https://github.com/natbkgift/flowbiz-client-ai-builder/actions
```

4. **Fix the issue**
   - Revert problematic commit if needed
   - Apply minimal fix
   - Test locally first

5. **Create HOTFIX PR**
```bash
git add .
git commit -m "hotfix: restore main to green - [issue description]"
git push origin hotfix/restore-main-green

# Open PR with title: "HOTFIX: [description]"
# Include full [BA][QA][SRE][DEV] sections
# Request immediate review
```

6. **Merge and verify**
   - Get PR approved
   - Merge to main
   - Verify CI passes
   - Resume AUTO_RUN

---

## 4. Workflow Approval Required

### Symptoms
- Workflows show "awaiting approval"
- First-time contributor PRs
- New workflow files added

### Response Steps

```bash
# Repository maintainer action required:
# 1. Review workflow changes carefully
# 2. Approve workflow run in Actions tab
# 3. Document as HUMAN_APPROVAL_REQUIRED in PR

# Status: HUMAN_APPROVAL_REQUIRED
# Reason: First-time workflow / New contributor
# Action: Maintainer approval needed
```

---

## 5. Rollback Procedures

### Revert Last Merge
```bash
git checkout main
git pull origin main

# Find the merge commit
git log --oneline -10

# Revert the merge
git revert -m 1 <merge-commit-sha>

# Push
git push origin main
```

### Emergency Production Rollback
```bash
# If deployment is automated:
# 1. Stop deployment process
# 2. Revert main branch
# 3. Trigger redeploy of last known good commit

# Manual:
git checkout <last-good-commit>
# Deploy this version
```

---

## 6. Cache Issues

### Clear GitHub Actions Cache
```bash
# Navigate to: 
# Settings → Actions → Caches
# Delete affected caches

# Or via API:
gh cache delete --all
```

### Clear Local Cache
```bash
rm -rf ~/.cache/pip
rm -rf .pytest_cache
rm -rf __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} +
```

---

## 7. Escalation

### Level 1: Self-Service (5-15 minutes)
- Check runbook
- Run commands locally
- Check recent CI logs

### Level 2: Team Discussion (15-60 minutes)
- Open GitHub issue
- Tag repository maintainers
- Share CI logs and error messages

### Level 3: Critical Incident (Immediate)
- Main branch broken > 1 hour
- Production deployment blocked
- Security vulnerability detected

**Escalation Command:**
```
Create GitHub issue with:
- Title: [CRITICAL] CI Failure - <description>
- Labels: bug, ci, priority:high
- Assignees: @natbkgift
- Body: Include CI logs, steps taken, current status
```

---

## 8. Monitoring & Prevention

### Daily Checks
- ✅ Main branch CI status
- ✅ Open PR CI status
- ✅ Security scan results
- ✅ Dependency audit status

### Weekly Reviews
- Review failed workflow patterns
- Update dependencies
- Review security advisories
- Update this RUNBOOK

### Automation
- AUTO_RUN controller monitors main branch
- Automatic notifications on failures
- Policy checks enforce standards

---

## Appendix: Common Errors

### Import Error: No module named 'apps'
```bash
# Fix: Install package in editable mode
pip install -e .
```

### Ruff: Command not found
```bash
# Fix: Install dev dependencies
pip install -e ".[dev]"
```

### Docker Build Fails: Cannot find Dockerfile
```bash
# Fix: Ensure you're in repository root
cd /path/to/flowbiz-client-ai-builder
docker build -t test .
```

### Pytest: No tests collected
```bash
# Fix: Ensure pytest can find tests/
pytest tests/ -v
```

---

**Last Updated:** 2025-12-27  
**Version:** 1.0 (Hotfix)  
**Maintained By:** Repository Team
