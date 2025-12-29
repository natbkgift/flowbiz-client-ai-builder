# Core Contracts - AI Builder System

## Overview

This document describes the core contracts (types, interfaces, and DTOs) that define the FlowBiz AI Builder platform. These contracts establish the foundation for implementing the Human-Inspired Engineering Model outlined in BLUEPRINT.md.

**Phase:** PR #3 - Core Contracts Only  
**Status:** Complete  
**Version:** 0.1.0

## Design Principles

1. **Contract-First**: Define interfaces before implementations
2. **Type-Safe**: Use Pydantic models for validation
3. **Adapter-Ready**: Enable mock → real implementation switching
4. **No Hard Dependencies**: Operate independently first

## Core Contract Categories

### 1. Agent Schemas (`packages/core/schemas/agents.py`)

Defines the Feature Squad Model with agent roles and responsibilities.

**Key Types:**
- `AgentRole`: Enum defining role types (BA, QA, SRE, DEV, UX, DATA, ORCHESTRATOR)
- `AgentStatus`: Enum for agent lifecycle (IDLE, ACTIVE, BLOCKED, COMPLETED, FAILED)
- `Agent`: Base agent with role, status, and assigned task
- `FeatureSquad`: Temporary squad assembled for a single feature
- Input models for each agent role:
  - `BusinessAnalystInput`: Problem statement and acceptance criteria
  - `QualityAssuranceInput`: Test plan and coverage
  - `SREInput`: Deployment and verification plan
  - `DeveloperInput`: Implementation notes and checks

**Purpose:**  
Enables multi-agent coordination where 1 Feature = 1 Temporary Squad.

### 2. Gate Schemas (`packages/core/schemas/gates.py`)

Defines the 6-gate validation pipeline from BLUEPRINT.md.

**Key Types:**
- `GateType`: Enum for gate stages (SAFETY, PLANNING, CI, STAGING, PRODUCTION, LEARNING)
- `GateStatus`: Enum for validation status (PENDING, PASSED, FAILED, SKIPPED)
- Gate result models:
  - `SafetyGateResult`: Gate -1 (forbidden paths, secrets, permissions)
  - `PlanningGateResult`: Gate 0 (PRD, test plan, deploy plan)
  - `CIGateResult`: Gate 1 (lint, tests, security, dependencies)
  - `StagingGateResult`: Gate 2 (staging deployment and smoke tests)
  - `ProductionGateResult`: Gate 3 (production deployment and verification)
  - `LearningGateResult`: Gate 4 (post-run reports and knowledge artifacts)
- `GatePipeline`: Complete pipeline with helper methods:
  - `is_ready_for_merge()`: Checks Safety, Planning, and CI gates
  - `is_production_ready()`: Checks all gates through Production

**Purpose:**  
Enforces evidence-based delivery with clear gate criteria.

### 3. Knowledge Schemas (`packages/core/schemas/knowledge.py`)

Defines automated knowledge sharing artifacts.

**Key Types:**
- `FeatureSummary`: High-level summary with key decisions
- `LessonsLearned`: What went well, what could improve, surprises
- `TestGaps`: Untested areas, flaky tests, missing test types
- `DeployNotes`: Deployment steps, environment changes, incidents
- `KnowledgeBundle`: Complete bundle of all artifacts for a feature
- `AutomationSuggestion`: Identifies automation opportunities (>3 repetitions)

**Purpose:**  
Replaces manual knowledge sharing sessions with auditable artifacts.

### 4. Workflow Schemas (`packages/core/schemas/workflow.py`)

Defines the Human-Inspired Engineering Model workflow phases.

**Key Types:**
- `WorkflowPhase`: Enum for phases (DISCOVERY, PLAN, BUILD, RELEASE, LEARN)
- `WorkflowStatus`: Enum for workflow state
- `PRWorkflow`: Tracks PR workflow execution
- Phase output models:
  - `DiscoveryPhaseOutput`: Requirements and problem statement
  - `PlanPhaseOutput`: Squad assembly and scope lock
  - `BuildPhaseOutput`: Code, tests, reviews, documentation
  - `ReleasePhaseOutput`: Staging and production deployment
  - `LearnPhaseOutput`: Knowledge artifacts and metrics
- `WorkflowExecution`: Complete workflow record across all phases
- `ApprovalRequired`: Human approval checkpoints with auto-approval support
  - `auto_approve_enabled`: Flag to enable automatic approval
  - `auto_approve()`: Method to automatically approve workflows
- `AutoApprovalConfig`: Configuration for auto-approval rules
  - `enabled`: Global toggle for auto-approval
  - `approval_types`: Whitelist of approval types that can be auto-approved
  - `excluded_workflows`: Blacklist of workflows that should never be auto-approved
  - `require_ci_pass`: Require CI to pass before auto-approval
  - `can_auto_approve()`: Method to check if approval can be auto-approved
- `HotfixWorkflow`: Special workflow for fail-safe hotfixes

**Purpose:**  
Implements Discovery → Plan → Build → Release → Learn model with automated approval capabilities.

### 5. Repository Schemas (`packages/core/schemas/repository.py`)

Defines multi-repository operations and management.

**Key Types:**
- `RepositoryType`: Enum for stack types (FASTAPI, NODEJS, WORKER, CRON, etc.)
- `RepositoryStatus`: Enum for repo lifecycle (PENDING, READY, ONBOARDING, ACTIVE, SUSPENDED)
- `Repository`: Repository definition in the platform
- `ReadinessCheckResult`: Results from automated readiness check
- `OnboardingPR`: Auto-generated PR to bring repo up to standards
- `Environment`: Environment configuration (dev, staging, prod)
- `EnvironmentType`: Enum for environment types
- Lock types for concurrency control:
  - `DeploymentLock`: Per-environment lock
  - `ProjectLock`: Per-project lock
- `Deployment`: Deployment record with verification status
- `VersionInfo`: Version tracking per environment

**Purpose:**  
Enables multi-repo platform with automated onboarding and safe deployments.

### 6. Webhook Schemas (`packages/core/schemas/webhooks.py`)

Defines normalized webhook event contracts for inbound signals.

**Key Types:**
- `WebhookSource`: Enum for webhook source systems
- `WebhookEvent`: Normalized event payload with metadata and raw payload
- `WebhookReceipt`: Acknowledgement response for webhook ingestion

**Purpose:**  
Establishes a contract-first model for receiving external events.

### 7. Notification Schemas (`packages/core/schemas/notifications.py`)

Defines notification contracts produced from inbound events.

**Key Types:**
- `NotificationChannel`: Enum for supported delivery channels
- `NotificationMessage`: Notification payload for delivery sinks

**Purpose:**  
Provides a consistent notification payload for alerting and audit trails.

## Integration Strategy

Per BLUEPRINT.md Section 9, these contracts enable:

1. **Independent Operation**: Platform operates without hard dependencies
2. **Adapter-Based Integration**: Easy to switch between mock and real implementations
3. **Contract-First**: Implementations will conform to these contracts
4. **Mock → Core Switch**: Can start with mocks, swap in real flowbiz-ai-core later

## Usage Examples

### Creating a Feature Squad

```python
from packages.core.schemas import (
    Agent, AgentRole, FeatureSquad, BusinessAnalystInput
)

# Create squad
squad = FeatureSquad(
    squad_id="squad-001",
    feature_name="API Performance Optimization",
    ba_agent=Agent(role=AgentRole.BA),
    qa_agent=Agent(role=AgentRole.QA),
    sre_agent=Agent(role=AgentRole.SRE),
    dev_agent=Agent(role=AgentRole.DEV)
)

# BA provides input
ba_input = BusinessAnalystInput(
    problem_statement="API response time exceeds SLA",
    acceptance_criteria=[
        "p95 response time < 200ms",
        "No degradation in error rate"
    ]
)
```

### Checking Gate Pipeline

```python
from packages.core.schemas import GatePipeline, SafetyGateResult, GateStatus

pipeline = GatePipeline(
    pr_number=123,
    safety_gate=SafetyGateResult(..., status=GateStatus.PASSED),
    planning_gate=PlanningGateResult(..., status=GateStatus.PASSED),
    ci_gate=CIGateResult(..., status=GateStatus.PASSED),
    # ... other gates
)

if pipeline.is_ready_for_merge():
    print("PR can be merged!")
```

### Tracking Workflow

```python
from packages.core.schemas import WorkflowExecution, WorkflowPhase

execution = WorkflowExecution(
    workflow_id="wf-001",
    pr_number=123,
    squad_id="squad-001",
    feature_name="Performance optimization",
    current_phase=WorkflowPhase.BUILD,
    status=WorkflowStatus.IN_PROGRESS
)
```

### Using Auto-Approval

```python
from packages.core.schemas import ApprovalRequired, AutoApprovalConfig

# Create an approval that can be auto-approved
approval = ApprovalRequired(
    approval_id="appr-001",
    workflow_id="wf-001",
    reason="Workflow approval for standard deployment",
    approval_type="workflow_approval",
    auto_approve_enabled=True
)

# Automatically approve it
approval.auto_approve()

# Configure auto-approval rules
config = AutoApprovalConfig(
    enabled=True,
    approval_types=["workflow_approval", "environment_approval"],
    excluded_workflows=["wf-critical-001"],
    require_ci_pass=True
)

# Check if an approval can be auto-approved
if config.can_auto_approve(approval, ci_passed=True):
    approval.auto_approve(approver="ci-bot")
```

## Next Steps

**NOT in PR #3 (Contract-Only):**
- ❌ Implementations of agents
- ❌ Adapters for GitHub/external services
- ❌ Gateway implementations
- ❌ API endpoints for contracts
- ❌ Orchestration logic
- ❌ Database schemas/persistence

**Future PRs:**
- PR #4: Mock adapters and basic orchestration
- PR #5: Agent implementations (BA, QA, SRE, DEV)
- PR #6: Gate validation implementations
- PR #7: Knowledge artifact generators
- Later: Real adapters for flowbiz-ai-core integration

## Testing

All contract types have comprehensive tests in `tests/`:
- `test_agents.py`: Agent and squad creation
- `test_gates.py`: Gate validation and pipeline
- `test_knowledge.py`: Knowledge artifacts
- `test_workflow.py`: Workflow phases
- `test_repository.py`: Multi-repo operations

Run tests:
```bash
pytest -q
```

## Validation

All schemas use Pydantic for:
- Type validation
- Required field enforcement
- Default value handling
- Serialization/deserialization
- JSON schema generation

## Exports

All contracts are exported from `packages.core.schemas.__init__.py` for easy import:

```python
from packages.core.schemas import (
    Agent, FeatureSquad, GatePipeline, 
    WorkflowExecution, Repository
)
```

## Compliance

This PR follows BLUEPRINT.md requirements:
- ✅ Contract-first approach (Section 9)
- ✅ Adapter-ready design (Section 9)
- ✅ No hard dependencies (Section 9)
- ✅ Evidence-based model (Section 1)
- ✅ Feature Squad Model (Section 4)
- ✅ Gate system (Section 3)
- ✅ Knowledge sharing (Section 6)
- ✅ Multi-repo support (Section 7)

---

**Document Status:** Complete  
**Last Updated:** 2025-12-27  
**Related:** BLUEPRINT.md, PROJECT_CONTRACT.md
