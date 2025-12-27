"""Core schema exports for AI Builder."""

# Base schemas
# AI Builder contracts
from packages.core.schemas.agents import (
    Agent,
    AgentRole,
    AgentStatus,
    BusinessAnalystInput,
    DeveloperInput,
    FeatureSquad,
    QualityAssuranceInput,
    SquadOutput,
    SREInput,
)
from packages.core.schemas.base import BaseResponse
from packages.core.schemas.error import ErrorResponse
from packages.core.schemas.gates import (
    CIGateResult,
    GatePipeline,
    GateStatus,
    GateType,
    LearningGateResult,
    PlanningGateResult,
    ProductionGateResult,
    SafetyGateResult,
    StagingGateResult,
)
from packages.core.schemas.health import HealthResponse, MetaResponse
from packages.core.schemas.knowledge import (
    AutomationSuggestion,
    DeployNotes,
    FeatureSummary,
    KnowledgeBundle,
    LessonsLearned,
    TestGaps,
)
from packages.core.schemas.repository import (
    Deployment,
    DeploymentLock,
    Environment,
    EnvironmentType,
    OnboardingPR,
    ProjectLock,
    ReadinessCheckResult,
    Repository,
    RepositoryStatus,
    RepositoryType,
    VersionInfo,
)
from packages.core.schemas.workflow import (
    ApprovalRequired,
    AutoApprovalConfig,
    BuildPhaseOutput,
    DiscoveryPhaseOutput,
    HotfixWorkflow,
    LearnPhaseOutput,
    PlanPhaseOutput,
    PRWorkflow,
    ReleasePhaseOutput,
    WorkflowExecution,
    WorkflowPhase,
    WorkflowStatus,
)

__all__ = [
    # Base schemas
    "BaseResponse",
    "ErrorResponse",
    "HealthResponse",
    "MetaResponse",
    # Agent schemas
    "Agent",
    "AgentRole",
    "AgentStatus",
    "BusinessAnalystInput",
    "DeveloperInput",
    "FeatureSquad",
    "QualityAssuranceInput",
    "SREInput",
    "SquadOutput",
    # Gate schemas
    "CIGateResult",
    "GatePipeline",
    "GateStatus",
    "GateType",
    "LearningGateResult",
    "PlanningGateResult",
    "ProductionGateResult",
    "SafetyGateResult",
    "StagingGateResult",
    # Knowledge schemas
    "AutomationSuggestion",
    "DeployNotes",
    "FeatureSummary",
    "KnowledgeBundle",
    "LessonsLearned",
    "TestGaps",
    # Repository schemas
    "Deployment",
    "DeploymentLock",
    "Environment",
    "EnvironmentType",
    "OnboardingPR",
    "ProjectLock",
    "ReadinessCheckResult",
    "Repository",
    "RepositoryStatus",
    "RepositoryType",
    "VersionInfo",
    # Workflow schemas
    "ApprovalRequired",
    "AutoApprovalConfig",
    "BuildPhaseOutput",
    "DiscoveryPhaseOutput",
    "HotfixWorkflow",
    "LearnPhaseOutput",
    "PlanPhaseOutput",
    "PRWorkflow",
    "ReleasePhaseOutput",
    "WorkflowExecution",
    "WorkflowPhase",
    "WorkflowStatus",
]
