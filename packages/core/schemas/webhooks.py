"""Webhook schemas for inbound event processing."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class WebhookSource(str, Enum):
    """Supported webhook sources."""

    GITHUB = "github"


class WebhookEvent(BaseModel):
    """Normalized webhook event payload."""

    event_id: str
    event_type: str
    source: WebhookSource
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = Field(default_factory=dict)


class WebhookReceipt(BaseModel):
    """Response after accepting a webhook event."""

    accepted: bool
    event_id: str
    source: WebhookSource
    event_type: str
    delivery_id: str | None = None
