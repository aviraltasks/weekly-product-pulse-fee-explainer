"""POST /api/integrations/gmail/send — Phase 7."""

from __future__ import annotations

import asyncio
import logging
import smtplib

from fastapi import APIRouter, HTTPException

from app.integrations.gmail.config import (
    gmail_send_configured,
    strict_recipients_only,
)
from app.integrations.gmail.recipients import resolve_recipients
from app.integrations.gmail.schemas import GmailSendRequest, GmailSendResponse
from app.integrations.gmail.service import send_email
from app.subscribers.store import list_subscribers

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/integrations/gmail", tags=["integrations", "gmail"])


@router.post("/send", response_model=GmailSendResponse)
async def post_gmail_send(body: GmailSendRequest) -> GmailSendResponse:
    """
    Send preview email to selected addresses. With GMAIL_STRICT_RECIPIENTS=true (default),
    only emails present in the subscribers store are accepted.
    """
    if not gmail_send_configured():
        raise HTTPException(
            status_code=503,
            detail=(
                "Gmail send not configured: set GMAIL_SMTP_USER and GMAIL_APP_PASSWORD "
                "(see apps/backend/.env.example)"
            ),
        )

    rows = list_subscribers()
    allowed_map = {r["email"].lower(): r["email"] for r in rows}
    strict = strict_recipients_only()

    send_to, rejected = resolve_recipients(
        body.to_emails,
        allowed_lower_to_canonical=allowed_map,
        strict=strict,
    )

    if strict and not send_to:
        raise HTTPException(
            status_code=400,
            detail=(
                "No valid recipients: all addresses must be in the subscribers list "
                f"(rejected: {rejected}). POST /api/subscribers first."
            ),
        )

    if not send_to:
        raise HTTPException(status_code=400, detail="No recipients after filtering")

    try:
        await asyncio.to_thread(
            send_email,
            to_emails=send_to,
            subject=body.subject,
            body_plain=body.body_plain,
            body_html=body.body_html,
        )
    except smtplib.SMTPException as e:
        logger.warning("SMTP error: %s", e)
        raise HTTPException(status_code=502, detail=f"SMTP error: {e}") from e
    except OSError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    return GmailSendResponse(
        sent_to=send_to,
        rejected=rejected,
        message="sent",
    )
