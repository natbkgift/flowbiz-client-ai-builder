"""Webhook watcher for GitHub events and notifications."""

import hashlib
import hmac
import json
import uuid
from typing import Any

from packages.core.logging import get_logger
from packages.core.notifications import NotificationDispatcher
from packages.core.schemas.notifications import NotificationChannel, NotificationMessage
from packages.core.schemas.webhooks import WebhookEvent, WebhookSource


class GitHubWebhookVerifier:
    """Verify GitHub webhook signatures when a secret is configured."""

    def __init__(self, secret: str | None) -> None:
        self._secret = secret

    def verify(self, signature_header: str | None, body: bytes) -> bool:
        if not self._secret:
            return True
        if not signature_header or not signature_header.startswith("sha256="):
            return False

        expected = hmac.new(self._secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        provided = signature_header.split("=", 1)[1]
        return hmac.compare_digest(expected, provided)


class WebhookWatcher:
    """Normalize inbound webhooks and dispatch notifications."""

    def __init__(self, dispatcher: NotificationDispatcher | None = None) -> None:
        self._dispatcher = dispatcher or NotificationDispatcher()
        self._logger = get_logger("webhook_watcher")

    def handle_github_event(
        self, event_type: str, delivery_id: str | None, payload: dict[str, Any]
    ) -> WebhookEvent:
        event_id = delivery_id or str(uuid.uuid4())
        event = WebhookEvent(
            event_id=event_id,
            event_type=event_type,
            source=WebhookSource.GITHUB,
            payload=payload,
        )

        self._logger.info(
            "webhook_event_id=%s source=%s event_type=%s",
            event.event_id,
            event.source.value,
            event.event_type,
        )
        self._dispatch_notification(event, delivery_id)
        return event

    def _dispatch_notification(self, event: WebhookEvent, delivery_id: str | None) -> None:
        subject = self._build_subject(event)
        body = self._build_body(event)
        metadata = self._build_metadata(event, delivery_id)

        message = NotificationMessage(
            notification_id=str(uuid.uuid4()),
            channel=NotificationChannel.LOG,
            subject=subject,
            body=body,
            event_id=event.event_id,
            metadata=metadata,
        )
        self._dispatcher.dispatch(message)

    def _build_subject(self, event: WebhookEvent) -> str:
        action = event.payload.get("action")
        repo = event.payload.get("repository", {}).get("full_name")
        parts = [event.event_type]
        if action:
            parts.append(action)
        if repo:
            parts.append(repo)
        return "github webhook: " + " ".join(parts)

    def _build_body(self, event: WebhookEvent) -> str:
        summary = {
            "event_type": event.event_type,
            "action": event.payload.get("action"),
            "repository": event.payload.get("repository", {}).get("full_name"),
        }
        return json.dumps(summary)

    def _build_metadata(self, event: WebhookEvent, delivery_id: str | None) -> dict[str, Any]:
        return {
            "source": event.source.value,
            "event_type": event.event_type,
            "delivery_id": delivery_id,
        }
