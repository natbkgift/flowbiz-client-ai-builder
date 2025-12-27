"""GitHub API Adapter following Blueprint v10 §9 (contract-first, adapter pattern)."""

import base64
import os
from typing import Any

import httpx


class GitHubError(Exception):
    """Base exception for GitHub adapter errors."""

    def __init__(self, message: str, status_code: int | None = None, response: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class GitHubAuthError(GitHubError):
    """Authentication error (401)."""

    ...


class GitHubForbiddenError(GitHubError):
    """Forbidden error (403)."""

    ...


class GitHubNotFoundError(GitHubError):
    """Not found error (404)."""

    ...


class GitHubValidationError(GitHubError):
    """Validation error (422)."""

    ...


class GitHubAdapter:
    """
    GitHub API adapter for creating branches, commits, and PRs.

    Implements contract-first design following Blueprint v10 §9.
    """

    def __init__(self, token: str | None = None, base_url: str = "https://api.github.com"):
        """
        Initialize GitHub adapter.

        Args:
            token: GitHub token (PAT or GitHub App token). If None, reads from GITHUB_TOKEN env var.
            base_url: GitHub API base URL. Default: https://api.github.com
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise GitHubAuthError(
                "GitHub token not provided. Set GITHUB_TOKEN environment variable "
                "or pass token parameter."
            )

        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30.0,
        )

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle HTTP error responses."""
        try:
            error_data = response.json()
        except Exception:
            error_data = {"message": response.text}

        message = error_data.get("message", "Unknown error")

        if response.status_code == 401:
            raise GitHubAuthError(
                f"Authentication failed: {message}. "
                "Please check your GITHUB_TOKEN is valid and has not expired.",
                status_code=401,
                response=error_data,
            )
        elif response.status_code == 403:
            raise GitHubForbiddenError(
                f"Forbidden: {message}. "
                "Please check your token has the required permissions (repo, workflow).",
                status_code=403,
                response=error_data,
            )
        elif response.status_code == 404:
            raise GitHubNotFoundError(
                f"Not found: {message}. "
                "Please check the repository slug and resource exist.",
                status_code=404,
                response=error_data,
            )
        elif response.status_code == 422:
            errors = error_data.get("errors", [])
            if errors:
                error_details = "; ".join([e.get("message", str(e)) for e in errors])
            else:
                error_details = message
            raise GitHubValidationError(
                f"Validation failed: {error_details}. "
                "Please check your input parameters.",
                status_code=422,
                response=error_data,
            )
        else:
            raise GitHubError(
                f"GitHub API error ({response.status_code}): {message}",
                status_code=response.status_code,
                response=error_data,
            )

    def create_branch(self, repo_slug: str, base_branch: str, new_branch: str) -> dict[str, Any]:
        """
        Create a new branch from a base branch.

        Args:
            repo_slug: Repository in format "owner/repo"
            base_branch: Base branch name (e.g., "main")
            new_branch: New branch name to create

        Returns:
            dict with branch information including:
                - ref: Full reference name
                - sha: Commit SHA
                - url: API URL for the reference

        Raises:
            GitHubAuthError: Authentication failed (401)
            GitHubForbiddenError: Permission denied (403)
            GitHubNotFoundError: Repository or base branch not found (404)
            GitHubValidationError: Invalid input (422)
        """
        # First, get the SHA of the base branch
        response = self.client.get(f"/repos/{repo_slug}/git/ref/heads/{base_branch}")
        if response.status_code != 200:
            self._handle_error(response)

        base_sha = response.json()["object"]["sha"]

        # Create the new branch
        response = self.client.post(
            f"/repos/{repo_slug}/git/refs",
            json={
                "ref": f"refs/heads/{new_branch}",
                "sha": base_sha,
            },
        )

        if response.status_code not in (200, 201):
            self._handle_error(response)

        data = response.json()
        return {
            "ref": data["ref"],
            "sha": data["object"]["sha"],
            "url": data["url"],
        }

    def create_commit(
        self, repo_slug: str, branch: str, file_path: str, content: str, message: str
    ) -> dict[str, Any]:
        """
        Create a commit with file content on a branch.

        Args:
            repo_slug: Repository in format "owner/repo"
            branch: Branch name to commit to
            file_path: Path to the file in the repository
            content: File content (will be base64 encoded)
            message: Commit message

        Returns:
            dict with commit information including:
                - sha: Commit SHA
                - message: Commit message
                - html_url: Web URL for the commit

        Raises:
            GitHubAuthError: Authentication failed (401)
            GitHubForbiddenError: Permission denied (403)
            GitHubNotFoundError: Repository or branch not found (404)
            GitHubValidationError: Invalid input (422)
        """
        # Get current file SHA if it exists (for updates)
        file_sha = None
        response = self.client.get(
            f"/repos/{repo_slug}/contents/{file_path}", params={"ref": branch}
        )
        if response.status_code == 200:
            file_sha = response.json().get("sha")

        # Encode content to base64
        content_bytes = content.encode("utf-8")
        encoded_content = base64.b64encode(content_bytes).decode("utf-8")

        # Create or update the file
        payload: dict[str, Any] = {
            "message": message,
            "content": encoded_content,
            "branch": branch,
        }
        if file_sha:
            payload["sha"] = file_sha

        response = self.client.put(
            f"/repos/{repo_slug}/contents/{file_path}",
            json=payload,
        )

        if response.status_code not in (200, 201):
            self._handle_error(response)

        data = response.json()
        commit_data = data["commit"]
        return {
            "sha": commit_data["sha"],
            "message": commit_data["message"],
            "html_url": commit_data["html_url"],
        }

    def create_pr(
        self, repo_slug: str, base: str, head: str, title: str, body: str
    ) -> dict[str, Any]:
        """
        Create a pull request.

        Args:
            repo_slug: Repository in format "owner/repo"
            base: Base branch name (e.g., "main")
            head: Head branch name (the branch with changes)
            title: PR title
            body: PR body/description

        Returns:
            dict with PR information including:
                - number: PR number
                - title: PR title
                - body: PR body
                - state: PR state (open, closed)
                - html_url: Web URL for the PR
                - user: PR author info

        Raises:
            GitHubAuthError: Authentication failed (401)
            GitHubForbiddenError: Permission denied (403)
            GitHubNotFoundError: Repository not found (404)
            GitHubValidationError: Invalid input or PR already exists (422)
        """
        response = self.client.post(
            f"/repos/{repo_slug}/pulls",
            json={
                "title": title,
                "body": body,
                "head": head,
                "base": base,
            },
        )

        if response.status_code not in (200, 201):
            self._handle_error(response)

        data = response.json()
        return {
            "number": data["number"],
            "title": data["title"],
            "body": data["body"],
            "state": data["state"],
            "html_url": data["html_url"],
            "user": {
                "login": data["user"]["login"],
                "id": data["user"]["id"],
            },
        }

    def get_pr_status(self, repo_slug: str, pr_number: int) -> dict[str, Any]:
        """
        Get PR status including merge status and review state.

        Args:
            repo_slug: Repository in format "owner/repo"
            pr_number: PR number

        Returns:
            dict with PR status including:
                - state: PR state (open, closed)
                - mergeable: Whether the PR can be merged
                - merged: Whether the PR has been merged
                - mergeable_state: Detailed merge state
                - draft: Whether the PR is a draft

        Raises:
            GitHubAuthError: Authentication failed (401)
            GitHubForbiddenError: Permission denied (403)
            GitHubNotFoundError: PR not found (404)
        """
        response = self.client.get(f"/repos/{repo_slug}/pulls/{pr_number}")

        if response.status_code != 200:
            self._handle_error(response)

        data = response.json()
        return {
            "state": data["state"],
            "mergeable": data.get("mergeable"),
            "merged": data["merged"],
            "mergeable_state": data.get("mergeable_state"),
            "draft": data.get("draft", False),
        }

    def get_check_runs(self, repo_slug: str, pr_number: int) -> list[dict[str, Any]]:
        """
        Get check runs for a PR (CI status, tests, etc.).

        Args:
            repo_slug: Repository in format "owner/repo"
            pr_number: PR number

        Returns:
            list of dicts with check run information:
                - id: Check run ID
                - name: Check run name
                - status: Status (queued, in_progress, completed)
                - conclusion: Conclusion if completed (success, failure, etc.)
                - html_url: Web URL for the check run

        Raises:
            GitHubAuthError: Authentication failed (401)
            GitHubForbiddenError: Permission denied (403)
            GitHubNotFoundError: PR not found (404)
        """
        # First get the PR to get the head SHA
        pr_response = self.client.get(f"/repos/{repo_slug}/pulls/{pr_number}")
        if pr_response.status_code != 200:
            self._handle_error(pr_response)

        head_sha = pr_response.json()["head"]["sha"]

        # Get check runs for the head SHA
        response = self.client.get(
            f"/repos/{repo_slug}/commits/{head_sha}/check-runs",
            headers={"Accept": "application/vnd.github+json"},
        )

        if response.status_code != 200:
            self._handle_error(response)

        data = response.json()
        check_runs = []
        for run in data.get("check_runs", []):
            check_runs.append({
                "id": run["id"],
                "name": run["name"],
                "status": run["status"],
                "conclusion": run.get("conclusion"),
                "html_url": run["html_url"],
            })

        return check_runs

    def __del__(self):
        """Clean up HTTP client on deletion."""
        if hasattr(self, "client"):
            self.client.close()
