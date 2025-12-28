# CONTROLS.md
## FlowBiz AI Builder — Control Framework (ISO / Audit)

### 1. Control Objectives
Ensure:
- Secure software delivery
- Traceable decision-making
- Prevention of unauthorized or unsafe automation

### 2. Control Domains

#### 2.1 Planning Controls (Gate 0)
- PRD / DoD existence
- Acceptance criteria defined
- Test and deployment plans documented

#### 2.2 CI Controls (Gate 1)
- Automated linting and testing
- Security and dependency scans
- Budget and policy enforcement

#### 2.3 Staging Controls (Gate 2)
- Deployment of PR SHA
- Smoke and regression tests
- Evidence collection

#### 2.4 Production Controls (Gate 3)
- Controlled deployment of main branch
- Automated verification
- Automatic rollback on failure

#### 2.5 Learning Controls (Gate 4)
- Post-run analysis
- Lessons learned documentation
- Continuous improvement feedback

### 3. Access & Security Controls
- Least-privilege access model
- Environment separation
- Secrets rotation and audit logging

### 4. Concurrency & Safety Controls
- Per-project execution locks
- Per-environment locks
- Idempotent execution guarantees

### 5. Control Effectiveness
Each control must be testable, observable, and auditable.
