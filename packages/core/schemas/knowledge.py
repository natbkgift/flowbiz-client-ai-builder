"""Knowledge artifact definitions for automated knowledge sharing."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FeatureSummary(BaseModel):
    """Automated feature summary artifact."""

    feature_name: str
    squad_id: str
    pr_number: int
    summary: str = Field(..., description="High-level summary of the feature")
    problem_solved: str = Field(..., description="Problem that was solved")
    solution_approach: str = Field(..., description="Approach taken to solve the problem")
    key_decisions: list[str] = Field(
        default_factory=list, description="Key technical decisions made"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LessonsLearned(BaseModel):
    """Lessons learned artifact."""

    feature_name: str
    squad_id: str
    pr_number: int
    what_went_well: list[str] = Field(default_factory=list, description="What went well")
    what_could_improve: list[str] = Field(
        default_factory=list, description="What could be improved"
    )
    surprises: list[str] = Field(default_factory=list, description="Unexpected findings")
    recommendations: list[str] = Field(
        default_factory=list, description="Recommendations for future work"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TestGaps(BaseModel):
    """Test gaps identification artifact."""

    feature_name: str
    squad_id: str
    pr_number: int
    untested_areas: list[str] = Field(
        default_factory=list, description="Areas not covered by tests"
    )
    flaky_tests: list[str] = Field(default_factory=list, description="Tests that are flaky")
    missing_test_types: list[str] = Field(
        default_factory=list, description="Types of tests that are missing (e.g., integration, e2e)"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Recommendations to close gaps"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DeployNotes(BaseModel):
    """Deployment notes artifact."""

    feature_name: str
    squad_id: str
    pr_number: int
    deployment_steps: list[str] = Field(..., description="Steps taken to deploy")
    environment_changes: list[str] = Field(
        default_factory=list, description="Environment changes required"
    )
    monitoring_setup: list[str] = Field(
        default_factory=list, description="Monitoring setup or changes"
    )
    rollback_tested: bool = Field(..., description="Whether rollback was tested")
    incidents: list[str] = Field(
        default_factory=list, description="Any incidents during deployment"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class KnowledgeBundle(BaseModel):
    """Complete knowledge bundle for a feature."""

    squad_id: str
    feature_name: str
    pr_number: int
    feature_summary: FeatureSummary
    lessons_learned: LessonsLearned
    test_gaps: TestGaps
    deploy_notes: DeployNotes
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AutomationSuggestion(BaseModel):
    """Suggestion for automation opportunities."""

    task_description: str = Field(..., description="Description of the repetitive task")
    times_repeated: int = Field(..., description="Number of times this task was repeated")
    estimated_time_per_occurrence: int = Field(
        ..., description="Estimated time in minutes per occurrence"
    )
    automation_approach: Optional[str] = Field(None, description="Suggested automation approach")
    priority: str = Field(..., description="Priority: high, medium, low")
    created_at: datetime = Field(default_factory=datetime.utcnow)
