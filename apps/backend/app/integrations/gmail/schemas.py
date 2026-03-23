"""Gmail send API body."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GmailSendRequest(BaseModel):
    """Use fields from `POST /api/preview/create` → `email` (include body_html for formatted mail)."""

    to_emails: list[str] = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    body_plain: str = Field(..., min_length=1)
    body_html: str | None = Field(
        default=None,
        description="Optional HTML part; Gmail shows this when present",
    )


class GmailSendResponse(BaseModel):
    sent_to: list[str]
    rejected: list[str] = Field(default_factory=list)
    message: str = "sent"
