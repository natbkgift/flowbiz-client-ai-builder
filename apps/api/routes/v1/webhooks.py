import json

from fastapi import APIRouter, Header, HTTPException, Request, status

from packages.core.config import settings
from packages.core.schemas.webhooks import WebhookReceipt, WebhookSource
from packages.core.webhook_watcher import GitHubWebhookVerifier, WebhookWatcher

router = APIRouter(prefix="/v1")


@router.post(
    "/webhooks/github",
    response_model=WebhookReceipt,
    status_code=status.HTTP_202_ACCEPTED,
)
async def github_webhook(
    request: Request,
    x_github_event: str | None = Header(default=None, alias="X-GitHub-Event"),
    x_github_delivery: str | None = Header(default=None, alias="X-GitHub-Delivery"),
    x_hub_signature_256: str | None = Header(default=None, alias="X-Hub-Signature-256"),
) -> WebhookReceipt:
    """Receive GitHub webhooks and dispatch notifications."""
    if not x_github_event:
        raise HTTPException(status_code=400, detail="Missing X-GitHub-Event header")

    body = await request.body()
    verifier = GitHubWebhookVerifier(settings.github_webhook_secret)
    if not verifier.verify(x_hub_signature_256, body):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    if body:
        try:
            payload = json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc
    else:
        payload = {}

    watcher = WebhookWatcher()
    event = watcher.handle_github_event(x_github_event, x_github_delivery, payload)

    return WebhookReceipt(
        accepted=True,
        event_id=event.event_id,
        source=WebhookSource.GITHUB,
        event_type=event.event_type,
        delivery_id=x_github_delivery,
    )
