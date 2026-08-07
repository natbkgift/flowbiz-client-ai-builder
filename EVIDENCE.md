# EVIDENCE.md
## FlowBiz AI Builder — Evidence & Audit Artifacts (v11)

### 1. Purpose
Defines evidence required for autonomous 24/7 delivery, incident review, and compliance verification.

Evidence requirements are execution-platform independent. They MUST NOT depend exclusively on GitHub Actions artifacts.

### 2. Evidence Categories

#### 2.1 Planning Evidence
- execution intent / PRD / DoD;
- acceptance criteria;
- test plan;
- deployment/rollback plan;
- resolved project ID and repository;
- exact target SHA/ref;
- approval decision when required.

#### 2.2 FlowBiz Runner Evidence
- Runner run ID;
- repository and exact SHA;
- lint/test/build command results;
- security/dependency scan outputs;
- migration rehearsal results when applicable;
- E2E/browser results when configured;
- start/end timestamps;
- Runner version/environment metadata;
- artifact checksum/SBOM/attestation when produced.

Legacy GitHub Actions evidence may be attached as supplemental evidence during migration but is not authoritative by itself under v11.

#### 2.3 Deployment Evidence
- production preflight;
- backup record;
- validated source SHA/artifact checksum;
- deployment run ID;
- release ID and previous release ID;
- migration result;
- service activation/restart result;
- local and public health/smoke results;
- rollback record when invoked.

#### 2.4 Runtime / Incident Evidence
- project/service health state;
- resource-guard deferrals;
- controlled-halt reason;
- bounded retry history;
- incident timeline and root cause where required.

#### 2.5 Learning Evidence
- post-run report;
- lessons learned;
- repeated-task automation opportunities;
- improvement proposal references.

### 3. Evidence Requirements
Evidence must be:
- immutable once finalized;
- timestamped;
- traceable to project, repository, exact SHA, run ID, and milestone;
- attributable to an actor/service identity;
- sufficient to reproduce the decision path;
- retained outside ephemeral CI workspaces before those workspaces are destroyed.

### 4. Evidence Storage
Initial single-VPS mode may store evidence under a protected Control Plane path such as:

```text
/opt/flowbiz/ci/evidence/<project>/<run-id>/
```

The implementation may later move evidence to object storage or a dedicated evidence service without changing the evidence contract.

Production applications and Runner jobs MUST NOT be able to alter finalized evidence outside their granted scope.

### 5. Retention Policy
- Evidence is retained according to organizational policy.
- Silent deletion or mutation of finalized evidence is prohibited.
- Cleanup policies must be explicit, auditable, and exclude evidence still required by active incidents/releases.

### 6. Audit Usage
Evidence must support:
- internal/external audits;
- release verification;
- incident/post-mortem analysis;
- rollback verification;
- autonomous-run review;
- migration from single-VPS to distributed infrastructure.
