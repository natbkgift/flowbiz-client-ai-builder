# POLICY.md
## FlowBiz AI Builder — Governance & Engineering Policy (ISO-Style)

### 1. Purpose
This document defines mandatory governance, engineering, and automation policies
for the FlowBiz AI Builder platform. These policies ensure safety, auditability,
repeatability, and regulatory readiness.

### 2. Scope
Applies to:
- All repositories managed by FlowBiz AI Builder
- All Pull Requests, CI/CD workflows, and deployments
- All AI agents and human operators

### 3. Core Policy Principles
- Evidence-driven execution
- Explicit human accountability
- Least privilege and safety-first operation
- No undocumented or irreversible actions

### 4. Automation Policy
- Automation is mandatory for any task repeated more than three (3) times
- Automation must be deterministic and idempotent
- Automation without rollback is prohibited

### 5. Pull Request Policy
- Every PR must map to exactly one approved milestone
- PR metadata and template completion are mandatory
- Non-compliant PRs must be blocked automatically

### 6. Approval & Authority
- AUTO_RUN_STRICT is the default operating mode
- AUTO_RUN_GUIDED requires explicit human authorization
- Production changes require auditable approval

### 7. Non-Compliance Handling
- Immediate halt of execution
- Preservation of system state
- Mandatory human review and documentation

### 8. Policy Review
This policy must be reviewed on a regular basis or after major incidents.
