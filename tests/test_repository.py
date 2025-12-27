"""Tests for repository schemas."""

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


def test_repository_creation():
    """Test repository creation."""
    repo = Repository(
        repo_id="repo-001",
        owner="natbkgift",
        name="flowbiz-client-ai-builder",
        full_name="natbkgift/flowbiz-client-ai-builder",
        repo_type=RepositoryType.FASTAPI,
        status=RepositoryStatus.ACTIVE,
    )
    assert repo.repo_id == "repo-001"
    assert repo.repo_type == RepositoryType.FASTAPI
    assert repo.status == RepositoryStatus.ACTIVE


def test_readiness_check_result():
    """Test readiness check result."""
    result = ReadinessCheckResult(
        repo_id="repo-001",
        has_pr_template=True,
        has_ci_workflow=True,
        has_required_files=True,
        follows_standards=True,
        has_health_endpoints=True,
        ready=True,
    )
    assert result.ready is True
    assert result.has_pr_template is True


def test_readiness_check_with_issues():
    """Test readiness check with issues found."""
    result = ReadinessCheckResult(
        repo_id="repo-001",
        has_pr_template=False,
        has_ci_workflow=True,
        has_required_files=True,
        follows_standards=False,
        issues_found=["Missing PR template", "Code style violations"],
        ready=False,
    )
    assert result.ready is False
    assert len(result.issues_found) == 2


def test_onboarding_pr():
    """Test onboarding PR."""
    pr = OnboardingPR(
        onboarding_id="onb-001",
        repo_id="repo-001",
        changes_needed=["Add PR template", "Add CI workflow", "Fix code style"],
    )
    assert pr.onboarding_id == "onb-001"
    assert len(pr.changes_needed) == 3
    assert pr.completed is False


def test_environment_creation():
    """Test environment creation."""
    env = Environment(
        environment_id="env-001",
        repo_id="repo-001",
        environment_type=EnvironmentType.PRODUCTION,
        url="https://api.example.com",
        requires_approval=True,
        approvers=["user1", "user2"],
    )
    assert env.environment_type == EnvironmentType.PRODUCTION
    assert env.requires_approval is True
    assert len(env.approvers) == 2


def test_deployment_lock():
    """Test deployment lock."""
    lock = DeploymentLock(
        lock_id="lock-001",
        repo_id="repo-001",
        environment=EnvironmentType.PRODUCTION,
        locked_by="workflow-123",
    )
    assert lock.environment == EnvironmentType.PRODUCTION
    assert lock.locked_by == "workflow-123"


def test_deployment():
    """Test deployment record."""
    deployment = Deployment(
        deployment_id="dep-001",
        repo_id="repo-001",
        environment=EnvironmentType.STAGING,
        commit_sha="abc123",
        pr_number=123,
        deployed_by="user1",
    )
    assert deployment.environment == EnvironmentType.STAGING
    assert deployment.commit_sha == "abc123"
    assert deployment.verified is False


def test_project_lock():
    """Test project lock."""
    lock = ProjectLock(
        lock_id="lock-001",
        repo_id="repo-001",
        operation="onboarding",
        locked_by="workflow-456",
    )
    assert lock.operation == "onboarding"
    assert lock.locked_by == "workflow-456"


def test_version_info():
    """Test version info."""
    version = VersionInfo(
        repo_id="repo-001",
        environment=EnvironmentType.PRODUCTION,
        version="1.2.3",
        commit_sha="abc123",
    )
    assert version.version == "1.2.3"
    assert version.environment == EnvironmentType.PRODUCTION


def test_repository_type_enum():
    """Test repository type enum values."""
    assert RepositoryType.FASTAPI == "fastapi"
    assert RepositoryType.NODEJS == "nodejs"
    assert RepositoryType.WORKER == "worker"


def test_repository_status_enum():
    """Test repository status enum values."""
    assert RepositoryStatus.PENDING == "pending"
    assert RepositoryStatus.READY == "ready"
    assert RepositoryStatus.ACTIVE == "active"


def test_environment_type_enum():
    """Test environment type enum values."""
    assert EnvironmentType.DEVELOPMENT == "dev"
    assert EnvironmentType.STAGING == "staging"
    assert EnvironmentType.PRODUCTION == "production"
