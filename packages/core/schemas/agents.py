"""Agent type definitions for Feature Squad Model."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """Agent roles in the Feature Squad Model."""

    BA = "ba"  # Business Analyst
    QA = "qa"  # Quality Assurance
    SRE = "sre"  # Site Reliability Engineer
    DEV = "dev"  # Developer
    UX = "ux"  # User Experience (optional)
    DATA = "data"  # Data Engineer (optional)
    ORCHESTRATOR = "orchestrator"  # Squad Lead


class AgentStatus(str, Enum):
    """Status of an agent in the squad."""

    IDLE = "idle"
    ACTIVE = "active"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


class Agent(BaseModel):
    """Base agent definition."""

    role: AgentRole
    status: AgentStatus = AgentStatus.IDLE
    assigned_task: Optional[str] = None
    metadata: dict[str, str] = Field(default_factory=dict)


class BusinessAnalystInput(BaseModel):
    """Input from BA Agent - Problem Statement and Acceptance Criteria."""

    problem_statement: str = Field(
        ..., description="Clear problem description and value proposition"
    )
    acceptance_criteria: list[str] = Field(
        ..., description="List of business acceptance criteria"
    )
    prd_link: Optional[str] = Field(None, description="Link to Product Requirements Document")
    dod_link: Optional[str] = Field(None, description="Link to Definition of Done")


class QualityAssuranceInput(BaseModel):
    """Input from QA Agent - Test Plan and Coverage."""

    tests_added: list[str] = Field(..., description="List of tests added or updated")
    smoke_coverage: bool = Field(..., description="Whether smoke tests cover the changes")
    regression_coverage: bool = Field(..., description="Whether regression tests cover the changes")
    test_plan_link: Optional[str] = None


class SREInput(BaseModel):
    """Input from SRE Agent - Deployment and Verification Plan."""

    deployment_impact: str = Field(..., description="Assessment of deployment impact")
    verify_steps: list[str] = Field(..., description="Steps to verify successful deployment")
    rollback_steps: list[str] = Field(..., description="Steps to rollback if deployment fails")
    monitoring_notes: Optional[str] = None


class DeveloperInput(BaseModel):
    """Input from Dev Agent - Implementation notes."""

    implementation_summary: str = Field(..., description="Summary of implementation approach")
    tests_updated: bool = Field(..., description="Whether tests were updated")
    manual_steps_added: bool = Field(False, description="Whether new manual steps were introduced")
    security_reviewed: bool = Field(..., description="Whether security impact was reviewed")
    local_testing_completed: bool = Field(..., description="Whether local testing was completed")


class FeatureSquad(BaseModel):
    """A temporary squad assembled for a single feature."""

    squad_id: str
    feature_name: str
    ba_agent: Agent
    qa_agent: Agent
    sre_agent: Agent
    dev_agent: Agent
    ux_agent: Optional[Agent] = None
    data_agent: Optional[Agent] = None
    orchestrator: Agent = Field(
        default_factory=lambda: Agent(role=AgentRole.ORCHESTRATOR, status=AgentStatus.ACTIVE)
    )
    status: AgentStatus = AgentStatus.IDLE


class SquadOutput(BaseModel):
    """Output from a Feature Squad."""

    squad_id: str
    feature_name: str
    ba_input: BusinessAnalystInput
    qa_input: QualityAssuranceInput
    sre_input: SREInput
    dev_input: DeveloperInput
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
