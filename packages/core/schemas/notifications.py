"""Notification schemas for event-driven alerts."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NotificationChannel(str, Enum):
    """Supported notification channels."""

    LOG = "log"


class NotificationMessage(BaseModel):
    """Notification payload delivered to sinks."""

    notification_id: str
    channel: NotificationChannel = NotificationChannel.LOG
    subject: str
    body: str
    event_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
