"""Notification dispatch utilities for webhook events."""

from typing import Protocol

from packages.core.logging import get_logger
from packages.core.schemas.notifications import NotificationMessage


class NotificationSink(Protocol):
    """Interface for delivering notifications to external systems."""

    def send(self, message: NotificationMessage) -> None:
        """Send a notification message."""


class LogNotificationSink:
    """Default sink that logs notification metadata."""

    def __init__(self) -> None:
        self._logger = get_logger("notifications")

    def send(self, message: NotificationMessage) -> None:
        self._logger.info(
            "notification_id=%s channel=%s subject=%s",
            message.notification_id,
            message.channel.value,
            message.subject,
        )


class NotificationDispatcher:
    """Dispatch notifications to configured sinks."""

    def __init__(self, sinks: list[NotificationSink] | None = None) -> None:
        self._sinks = sinks or [LogNotificationSink()]

    def dispatch(self, message: NotificationMessage) -> None:
        for sink in self._sinks:
            sink.send(message)
