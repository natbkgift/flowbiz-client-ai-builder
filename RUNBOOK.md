# RUNBOOK — FlowBiz AI Builder

**Operational Procedures for CI/CD and Production**

---

## 1. Quick Reference

### CI Failure - What to Do

```bash
# Step 1: Check which job failed
Go to PR → Checks tab → Click failed job

# Step 2: Read the error logs
Identify the specific failure (lint/test/security/build)

# Step 3: Fix locally
Run the same command locally to reproduce

# Step 4: Verify fix
Run CI checks locally before pushing
```

### Common CI Failures

| Failure Type | Quick Fix |
|--------------|-----------|
| Lint failed | Run `ruff check . --fix` then `ruff format .` |
| Tests failed | Run `pytest -v` to see which tests failed |
| Security scan | Check gitleaks output for secrets, run `pip-audit` |
| Build failed | Check Dockerfile and dependencies |

---

## 2. CI Workflow Troubleshooting

### Lint Job Failed

**Symptoms:**
- ❌ Ruff check failed
- ❌ Ruff format check failed

**Diagnosis:**
```bash
# Run locally to see issues
ruff check .
ruff format --check .
```

**Fix:**
```bash
# Auto-fix most issues
ruff check . --fix

# Format code
ruff format .

# Verify
ruff check .
ruff format --check .

# Commit and push
git add .
git commit -m "Fix lint issues"
git push
```

**Prevention:**
- Set up pre-commit hooks
- Configure IDE to use ruff
- Run linter before committing

---

### Test Job Failed

**Symptoms:**
- ❌ One or more tests failing
- ❌ Test coverage dropped

**Diagnosis:**
```bash
# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_file.py -v

# Run with full traceback
pytest -v --tb=long

# Run with debugger
pytest --pdb
```

**Fix:**
1. **Read the test output carefully**
   - Identify which test(s) failed
   - Look at assertion errors
   - Check for missing fixtures or dependencies

2. **Fix the failing tests**
   ```bash
   # Edit the test or code
   # Re-run to verify
   pytest tests/test_file.py -v
   ```

3. **Commit and push**
   ```bash
   git add .
   git commit -m "Fix failing tests"
   git push
   ```

**Prevention:**
- Always run tests before pushing
- Write tests alongside code
- Keep tests simple and focused

---

### Security Scan Failed

**Symptoms:**
- ❌ Gitleaks detected secrets
- ❌ pip-audit found vulnerabilities

**Gitleaks Failure:**

**Diagnosis:**
```bash
# Install gitleaks locally
brew install gitleaks  # macOS
# or download from https://github.com/gitleaks/gitleaks

# Scan for secrets
gitleaks detect --verbose
```

### Issue: Gitleaks Detected Secrets in History

**⚠️ CRITICAL:** If secrets were committed historically, you must:
1. Rotate/revoke the compromised secret immediately
2. Remove from code and use environment variables
3. Use `git filter-repo` (modern tool) or regenerate repository

**Note:** `git filter-branch` is deprecated. Use `git filter-repo` instead:
```bash
# Install git-filter-repo
pip install git-filter-repo

# Remove file from history
git filter-repo --path path/to/secret-file --invert-paths

# Force push (coordinate with team first!)
git push --force
```

**pip-audit Failure:**

**Diagnosis:**
```bash
# Install pip-audit
pip install pip-audit

# Scan dependencies
pip-audit

# Check specific package
pip-audit | grep package-name
```

**Fix:**
```bash
# Update vulnerable package
pip install --upgrade vulnerable-package

# Update pyproject.toml
# Then test that nothing broke
pytest -v

# Commit and push
git add pyproject.toml
git commit -m "Update vulnerable dependency"
git push
```

**Prevention:**
- Never commit secrets
- Use `.env` files (in `.gitignore`)
- Regularly update dependencies
- Use `pip-audit` in pre-commit

---

### Build Job Failed

**Python Build Failure:**

**Diagnosis:**
```bash
# Try building locally
pip install build
python -m build
```

**Fix:**
```bash
# Check pyproject.toml syntax
# Check that all required fields are present
# Verify package structure

# Common issues:
# - Missing __init__.py files
# - Wrong package paths in pyproject.toml
# - Missing dependencies in [project.dependencies]

# After fixing
python -m build
ls -lh dist/
```

**Docker Build Failure:**

**Diagnosis:**
```bash
# Build locally with verbose output
docker build -t test .

# Check specific layer
docker build -t test . --target <stage-name>
```

**Fix:**
```bash
# Common issues:
# - Base image not available
# - COPY path incorrect
# - Missing dependencies
# - Port conflicts

# Test the fix
docker build -t test .
docker run -p 8000:8000 test

# Verify container works
curl http://localhost:8000/healthz
```

**Prevention:**
- Test Docker builds locally before pushing
- Use multi-stage builds
- Keep Dockerfile simple
- Document any special requirements

---

## 3. Local Development Setup

### Initial Setup

```bash
# Clone repository (replace with your repository URL)
git clone https://github.com/your-org/flowbiz-client-ai-builder.git
cd flowbiz-client-ai-builder

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -e ".[dev]"

# Verify setup
pytest -v
ruff check .
```

### Pre-Push Checklist

```bash
# 1. Run linter
ruff check . --fix
ruff format .

# 2. Run tests
pytest -v

# 3. Run security scan
pip-audit

# 4. Build package
python -m build

# 5. Build Docker (if changed)
docker build -t test .

# All green? Push!
git push
```

---

## 4. Environment Variables

### Required for Local Development

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your values
# Example:
FLOWBIZ_SERVICE_NAME=flowbiz-ai-builder
FLOWBIZ_VERSION=0.1.0
FLOWBIZ_LOG_LEVEL=INFO
```

### Required for CI/CD

Set these in GitHub Secrets:
- `GITHUB_TOKEN` (automatic, no need to set)
- `AUTORUN_GH_TOKEN` (if using AUTO_RUN controller)

---

## 5. Deployment Procedures

### Deploy to Development

```bash
# Via Docker Compose
docker-compose up -d

# Verify
curl http://localhost:8000/healthz
```

### Deploy to Staging *(Future)*

```bash
# TBD - Will be automated via GitHub Actions
```

### Deploy to Production *(Future)*

```bash
# TBD - Will be automated via GitHub Actions
# With approval gates and rollback procedures
```

---

## 6. Monitoring and Alerts

### Health Checks

```bash
# Check service health
curl http://localhost:8000/healthz

# Expected response:
# {"status": "ok", "service": "flowbiz-ai-builder", "version": "0.1.0"}
```

### Logs

```bash
# View Docker logs
docker-compose logs -f

# View specific service
docker-compose logs -f api
```

---

## 7. Rollback Procedures

### Rolling Back a PR

```bash
# If merged PR causes issues
git revert <commit-hash>
git push origin main

# This creates a new commit that undoes the changes
```

### Emergency Rollback *(Future)*

```bash
# TBD - Will be automated
# Automatic rollback on failed health checks
```

---

## 8. Common Issues and Solutions

### Issue: Port Already in Use

**Solution:**
```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Issue: Docker Out of Space

**Solution:**
```bash
# Clean up Docker
docker system prune -a --volumes

# Remove unused images
docker image prune -a
```

### Issue: Dependency Conflicts

**Solution:**
```bash
# Clear pip cache
pip cache purge

# Recreate virtual environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

---

## 9. Emergency Contacts

### When CI is Down
- Check GitHub Status: https://www.githubstatus.com/
- Contact: DevOps team

### When Security Scan Fails
- Rotate secrets immediately
- Report to security team
- Document in incident log

### When Production is Down *(Future)*
- TBD - Incident response procedures
- TBD - On-call rotation

---

## 10. References

- **BLUEPRINT.md** — Engineering philosophy and model
- **PR_POLICY.md** — PR requirements and process
- **GitHub Actions** — Workflow files in `.github/workflows/`
- **GitHub Status** — https://www.githubstatus.com/

---

**Remember:** When in doubt, check the logs first. Most issues have clear error messages.
