"""Tests for agent schemas."""

from packages.core.schemas.agents import (
    Agent,
    AgentRole,
    AgentStatus,
    BusinessAnalystInput,
    DeveloperInput,
    FeatureSquad,
    QualityAssuranceInput,
    SREInput,
)


def test_agent_creation():
    """Test creating an agent."""
    agent = Agent(role=AgentRole.DEV, status=AgentStatus.ACTIVE, assigned_task="Implement feature")
    assert agent.role == AgentRole.DEV
    assert agent.status == AgentStatus.ACTIVE
    assert agent.assigned_task == "Implement feature"


def test_agent_default_status():
    """Test agent has default IDLE status."""
    agent = Agent(role=AgentRole.BA)
    assert agent.status == AgentStatus.IDLE


def test_business_analyst_input():
    """Test BA input creation."""
    ba_input = BusinessAnalystInput(
        problem_statement="Need to improve performance",
        acceptance_criteria=["Response time < 200ms", "No errors in logs"],
    )
    assert ba_input.problem_statement == "Need to improve performance"
    assert len(ba_input.acceptance_criteria) == 2


def test_quality_assurance_input():
    """Test QA input creation."""
    qa_input = QualityAssuranceInput(
        tests_added=["test_performance.py", "test_integration.py"],
        smoke_coverage=True,
        regression_coverage=True,
    )
    assert len(qa_input.tests_added) == 2
    assert qa_input.smoke_coverage is True


def test_sre_input():
    """Test SRE input creation."""
    sre_input = SREInput(
        deployment_impact="Low impact, backward compatible",
        verify_steps=["Check health endpoint", "Monitor logs"],
        rollback_steps=["Revert commit", "Restart service"],
    )
    assert sre_input.deployment_impact == "Low impact, backward compatible"
    assert len(sre_input.verify_steps) == 2


def test_developer_input():
    """Test Dev input creation."""
    dev_input = DeveloperInput(
        implementation_summary="Optimized database queries",
        tests_updated=True,
        security_reviewed=True,
        local_testing_completed=True,
    )
    assert dev_input.implementation_summary == "Optimized database queries"
    assert dev_input.tests_updated is True
    assert dev_input.manual_steps_added is False


def test_feature_squad_creation():
    """Test creating a feature squad."""
    squad = FeatureSquad(
        squad_id="squad-001",
        feature_name="Performance improvements",
        ba_agent=Agent(role=AgentRole.BA),
        qa_agent=Agent(role=AgentRole.QA),
        sre_agent=Agent(role=AgentRole.SRE),
        dev_agent=Agent(role=AgentRole.DEV),
    )
    assert squad.squad_id == "squad-001"
    assert squad.feature_name == "Performance improvements"
    assert squad.orchestrator.role == AgentRole.ORCHESTRATOR


def test_agent_role_enum():
    """Test agent role enum values."""
    assert AgentRole.BA == "ba"
    assert AgentRole.QA == "qa"
    assert AgentRole.SRE == "sre"
    assert AgentRole.DEV == "dev"


def test_agent_status_enum():
    """Test agent status enum values."""
    assert AgentStatus.IDLE == "idle"
    assert AgentStatus.ACTIVE == "active"
    assert AgentStatus.COMPLETED == "completed"
