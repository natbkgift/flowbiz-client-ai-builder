"""Tests for GitHub API adapter."""

import base64
import os
from unittest.mock import MagicMock, patch

import httpx
import pytest

from packages.core.adapters.github_adapter import (
    GitHubAdapter,
    GitHubAuthError,
    GitHubForbiddenError,
    GitHubNotFoundError,
    GitHubValidationError,
)


@pytest.fixture
def github_adapter():
    """Create a GitHub adapter with a test token."""
    with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token_123"}):
        adapter = GitHubAdapter()
        yield adapter
        adapter.client.close()


@pytest.fixture
def mock_response():
    """Create a mock HTTP response."""

    def _create_response(status_code: int, json_data: dict):
        response = MagicMock(spec=httpx.Response)
        response.status_code = status_code
        response.json.return_value = json_data
        response.text = str(json_data)
        return response

    return _create_response


def test_adapter_initialization_with_token():
    """Test adapter initialization with explicit token."""
    adapter = GitHubAdapter(token="explicit_token")
    assert adapter.token == "explicit_token"
    assert adapter.base_url == "https://api.github.com"
    adapter.client.close()


def test_adapter_initialization_from_env():
    """Test adapter initialization from environment variable."""
    with patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"}):
        adapter = GitHubAdapter()
        assert adapter.token == "env_token"
        adapter.client.close()


def test_adapter_initialization_without_token():
    """Test adapter initialization fails without token."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(GitHubAuthError) as exc_info:
            GitHubAdapter()
        assert "GitHub token not provided" in str(exc_info.value)


def test_adapter_custom_base_url():
    """Test adapter with custom base URL."""
    adapter = GitHubAdapter(token="test_token", base_url="https://github.enterprise.com/api/v3")
    assert adapter.base_url == "https://github.enterprise.com/api/v3"
    adapter.client.close()


def test_create_branch_success(github_adapter, mock_response):
    """Test successful branch creation."""
    # Mock getting base branch SHA
    base_ref_response = mock_response(
        200, {"ref": "refs/heads/main", "object": {"sha": "base_sha_123"}}
    )

    # Mock creating new branch
    create_ref_response = mock_response(
        201,
        {
            "ref": "refs/heads/feature-branch",
            "object": {"sha": "base_sha_123"},
            "url": "https://api.github.com/repos/owner/repo/git/refs/heads/feature-branch",
        },
    )

    with patch.object(github_adapter.client, "get", return_value=base_ref_response):
        with patch.object(github_adapter.client, "post", return_value=create_ref_response):
            result = github_adapter.create_branch("owner/repo", "main", "feature-branch")

    assert result["ref"] == "refs/heads/feature-branch"
    assert result["sha"] == "base_sha_123"
    assert "url" in result


def test_create_commit_new_file(github_adapter, mock_response):
    """Test creating a commit with a new file."""
    # Mock file doesn't exist (404)
    get_file_response = mock_response(404, {"message": "Not Found"})

    # Mock successful commit
    commit_response = mock_response(
        201,
        {
            "commit": {
                "sha": "commit_sha_123",
                "message": "Add new file",
                "html_url": "https://github.com/owner/repo/commit/commit_sha_123",
            }
        },
    )

    with patch.object(github_adapter.client, "get", return_value=get_file_response):
        with patch.object(github_adapter.client, "put", return_value=commit_response):
            result = github_adapter.create_commit(
                "owner/repo", "feature-branch", "src/test.py", "print('hello')", "Add new file"
            )

    assert result["sha"] == "commit_sha_123"
    assert result["message"] == "Add new file"
    assert result["html_url"].startswith("https://github.com")


def test_create_commit_update_file(github_adapter, mock_response):
    """Test creating a commit that updates an existing file."""
    # Mock file exists
    get_file_response = mock_response(
        200,
        {"sha": "existing_file_sha", "content": base64.b64encode(b"old content").decode("utf-8")},
    )

    # Mock successful commit
    commit_response = mock_response(
        200,
        {
            "commit": {
                "sha": "commit_sha_456",
                "message": "Update file",
                "html_url": "https://github.com/owner/repo/commit/commit_sha_456",
            }
        },
    )

    with patch.object(github_adapter.client, "get", return_value=get_file_response):
        with patch.object(github_adapter.client, "put", return_value=commit_response):
            result = github_adapter.create_commit(
                "owner/repo", "feature-branch", "src/test.py", "print('updated')", "Update file"
            )

    assert result["sha"] == "commit_sha_456"
    assert result["message"] == "Update file"


def test_create_pr_success(github_adapter, mock_response):
    """Test successful PR creation."""
    pr_response = mock_response(
        201,
        {
            "number": 42,
            "title": "Feature: Add awesome feature",
            "body": "This PR adds an awesome feature",
            "state": "open",
            "html_url": "https://github.com/owner/repo/pull/42",
            "user": {"login": "octocat", "id": 1},
        },
    )

    with patch.object(github_adapter.client, "post", return_value=pr_response):
        result = github_adapter.create_pr(
            "owner/repo",
            "main",
            "feature-branch",
            "Feature: Add awesome feature",
            "This PR adds an awesome feature",
        )

    assert result["number"] == 42
    assert result["title"] == "Feature: Add awesome feature"
    assert result["state"] == "open"
    assert result["html_url"] == "https://github.com/owner/repo/pull/42"
    assert result["user"]["login"] == "octocat"


def test_get_pr_status_success(github_adapter, mock_response):
    """Test getting PR status."""
    pr_status_response = mock_response(
        200,
        {
            "state": "open",
            "mergeable": True,
            "merged": False,
            "mergeable_state": "clean",
            "draft": False,
        },
    )

    with patch.object(github_adapter.client, "get", return_value=pr_status_response):
        result = github_adapter.get_pr_status("owner/repo", 42)

    assert result["state"] == "open"
    assert result["mergeable"] is True
    assert result["merged"] is False
    assert result["mergeable_state"] == "clean"
    assert result["draft"] is False


def test_get_check_runs_success(github_adapter, mock_response):
    """Test getting check runs for a PR."""
    # Mock PR response
    pr_response = mock_response(200, {"head": {"sha": "head_sha_123"}})

    # Mock check runs response
    check_runs_response = mock_response(
        200,
        {
            "check_runs": [
                {
                    "id": 1,
                    "name": "build",
                    "status": "completed",
                    "conclusion": "success",
                    "html_url": "https://github.com/owner/repo/runs/1",
                },
                {
                    "id": 2,
                    "name": "test",
                    "status": "completed",
                    "conclusion": "success",
                    "html_url": "https://github.com/owner/repo/runs/2",
                },
                {
                    "id": 3,
                    "name": "lint",
                    "status": "in_progress",
                    "conclusion": None,
                    "html_url": "https://github.com/owner/repo/runs/3",
                },
            ]
        },
    )

    with patch.object(github_adapter.client, "get", side_effect=[pr_response, check_runs_response]):
        result = github_adapter.get_check_runs("owner/repo", 42)

    assert len(result) == 3
    assert result[0]["name"] == "build"
    assert result[0]["status"] == "completed"
    assert result[0]["conclusion"] == "success"
    assert result[2]["status"] == "in_progress"
    assert result[2]["conclusion"] is None


def test_error_handling_401_auth(github_adapter, mock_response):
    """Test handling of 401 authentication error."""
    error_response = mock_response(401, {"message": "Bad credentials"})

    with patch.object(github_adapter.client, "get", return_value=error_response):
        with pytest.raises(GitHubAuthError) as exc_info:
            github_adapter.create_branch("owner/repo", "main", "feature")

        assert "Authentication failed" in str(exc_info.value)
        assert "check your GITHUB_TOKEN" in str(exc_info.value)
        assert exc_info.value.status_code == 401


def test_error_handling_403_forbidden(github_adapter, mock_response):
    """Test handling of 403 forbidden error."""
    error_response = mock_response(403, {"message": "Resource not accessible by integration"})

    with patch.object(github_adapter.client, "post", return_value=error_response):
        with pytest.raises(GitHubForbiddenError) as exc_info:
            github_adapter.create_pr("owner/repo", "main", "feature", "Title", "Body")

        assert "Forbidden" in str(exc_info.value)
        assert "permissions" in str(exc_info.value)
        assert exc_info.value.status_code == 403


def test_error_handling_404_not_found(github_adapter, mock_response):
    """Test handling of 404 not found error."""
    error_response = mock_response(404, {"message": "Not Found"})

    with patch.object(github_adapter.client, "get", return_value=error_response):
        with pytest.raises(GitHubNotFoundError) as exc_info:
            github_adapter.get_pr_status("owner/repo", 999)

        assert "Not found" in str(exc_info.value)
        assert "check the repository slug" in str(exc_info.value)
        assert exc_info.value.status_code == 404


def test_error_handling_422_validation(github_adapter, mock_response):
    """Test handling of 422 validation error."""
    error_response = mock_response(
        422,
        {
            "message": "Validation Failed",
            "errors": [{"message": "Reference already exists"}, {"message": "Invalid branch name"}],
        },
    )

    with patch.object(
        github_adapter.client,
        "get",
        return_value=mock_response(200, {"ref": "refs/heads/main", "object": {"sha": "sha123"}}),
    ):
        with patch.object(github_adapter.client, "post", return_value=error_response):
            with pytest.raises(GitHubValidationError) as exc_info:
                github_adapter.create_branch("owner/repo", "main", "existing-branch")

            assert "Validation failed" in str(exc_info.value)
            assert "Reference already exists" in str(exc_info.value)
            assert exc_info.value.status_code == 422


def test_complete_workflow(github_adapter, mock_response):
    """Test complete workflow: branch -> commit -> PR -> status."""
    # 1. Create branch
    with patch.object(
        github_adapter.client,
        "get",
        return_value=mock_response(200, {"ref": "refs/heads/main", "object": {"sha": "base_sha"}}),
    ):
        with patch.object(
            github_adapter.client,
            "post",
            return_value=mock_response(
                201,
                {
                    "ref": "refs/heads/feature",
                    "object": {"sha": "base_sha"},
                    "url": "https://api.github.com/repos/owner/repo/git/refs/heads/feature",
                },
            ),
        ):
            branch_result = github_adapter.create_branch("owner/repo", "main", "feature")
            assert branch_result["ref"] == "refs/heads/feature"

    # 2. Create commit
    with patch.object(github_adapter.client, "get", return_value=mock_response(404, {})):
        with patch.object(
            github_adapter.client,
            "put",
            return_value=mock_response(
                201,
                {
                    "commit": {
                        "sha": "commit_sha",
                        "message": "Add feature",
                        "html_url": "https://github.com/owner/repo/commit/commit_sha",
                    }
                },
            ),
        ):
            commit_result = github_adapter.create_commit(
                "owner/repo", "feature", "feature.py", "code", "Add feature"
            )
            assert commit_result["sha"] == "commit_sha"

    # 3. Create PR
    with patch.object(
        github_adapter.client,
        "post",
        return_value=mock_response(
            201,
            {
                "number": 1,
                "title": "Feature",
                "body": "Description",
                "state": "open",
                "html_url": "https://github.com/owner/repo/pull/1",
                "user": {"login": "user", "id": 1},
            },
        ),
    ):
        pr_result = github_adapter.create_pr(
            "owner/repo", "main", "feature", "Feature", "Description"
        )
        assert pr_result["number"] == 1

    # 4. Get PR status
    with patch.object(
        github_adapter.client,
        "get",
        return_value=mock_response(
            200,
            {
                "state": "open",
                "mergeable": True,
                "merged": False,
                "mergeable_state": "clean",
                "draft": False,
            },
        ),
    ):
        status_result = github_adapter.get_pr_status("owner/repo", 1)
        assert status_result["state"] == "open"
        assert status_result["mergeable"] is True
