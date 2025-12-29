import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from apps.api.main import app
from packages.core.config import settings
from packages.core.notifications import NotificationDispatcher
from packages.core.webhook_watcher import GitHubWebhookVerifier, WebhookWatcher

client = TestClient(app)


def _build_signature(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


class DummySink:
    def __init__(self) -> None:
        self.messages = []

    def send(self, message) -> None:
        self.messages.append(message)


def test_github_webhook_verifier_allows_no_secret():
    verifier = GitHubWebhookVerifier(secret=None)
    assert verifier.verify(signature_header=None, body=b"{}") is True


def test_github_webhook_verifier_rejects_bad_signature():
    verifier = GitHubWebhookVerifier(secret="secret")
    assert verifier.verify(signature_header="sha256=bad", body=b"{}") is False


def test_webhook_watcher_dispatches_notification():
    sink = DummySink()
    dispatcher = NotificationDispatcher([sink])
    watcher = WebhookWatcher(dispatcher)

    event = watcher.handle_github_event("pull_request", "delivery-1", {"action": "opened"})

    assert event.event_id == "delivery-1"
    assert len(sink.messages) == 1
    assert sink.messages[0].event_id == event.event_id


def test_github_webhook_endpoint_accepts_without_secret(monkeypatch):
    monkeypatch.setattr(settings, "github_webhook_secret", None)
    response = client.post(
        "/v1/webhooks/github",
        headers={"X-GitHub-Event": "pull_request"},
        json={"action": "opened"},
    )

    assert response.status_code == 202
    data = response.json()
    assert data["accepted"] is True
    assert data["event_type"] == "pull_request"


def test_github_webhook_endpoint_rejects_missing_event_header(monkeypatch):
    monkeypatch.setattr(settings, "github_webhook_secret", None)
    response = client.post("/v1/webhooks/github", json={})
    assert response.status_code == 400


def test_github_webhook_endpoint_rejects_invalid_json(monkeypatch):
    monkeypatch.setattr(settings, "github_webhook_secret", None)
    response = client.post(
        "/v1/webhooks/github",
        headers={"X-GitHub-Event": "pull_request"},
        content=b"{not json",
    )
    assert response.status_code == 400


def test_github_webhook_endpoint_rejects_invalid_signature(monkeypatch):
    monkeypatch.setattr(settings, "github_webhook_secret", "secret")
    body = json.dumps({"action": "opened"}).encode("utf-8")
    response = client.post(
        "/v1/webhooks/github",
        headers={
            "X-GitHub-Event": "pull_request",
            "X-Hub-Signature-256": "sha256=bad",
        },
        content=body,
    )
    assert response.status_code == 401


def test_github_webhook_endpoint_accepts_valid_signature(monkeypatch):
    secret = "secret"
    monkeypatch.setattr(settings, "github_webhook_secret", secret)
    body = json.dumps({"action": "opened"}).encode("utf-8")
    signature = _build_signature(secret, body)

    response = client.post(
        "/v1/webhooks/github",
        headers={
            "X-GitHub-Event": "pull_request",
            "X-Hub-Signature-256": signature,
        },
        content=body,
    )
    assert response.status_code == 202
