"""Preview package DTO — single payload for UI, Doc append (Phase 6), email (Phase 7)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.pulse.schemas import PulseGenerateResponse


class AsOnBlock(BaseModel):
    """Timestamp shown as 'As on — …' in Doc/email."""

    iso_utc: str = Field(..., description="UTC instant when preview was created")
    display: str = Field(..., description="Human line, e.g. 17 Mar 2025, 18:45 IST")


class DocAppendPayload(BaseModel):
    """MCP #1 JSON shape (see SAMPLE_PULSE_OUTPUTS.md §A)."""

    date: str = Field(..., description="Same as As on display for this preview")
    weekly_pulse: str = Field(..., description="Leadership weekly note (≤250 words cap in pipeline)")
    fee_scenario: str = ""
    explanation_bullets: list[str] = Field(default_factory=list)
    source_links: list[str] = Field(default_factory=list)
    last_checked_iso: str = ""
    weekly_pulse_n: int | None = Field(
        default=None,
        description="Serial N for this preview (for Doc/email headers)",
    )


class EmailPreview(BaseModel):
    subject: str
    body_plain: str
    body_html: str = Field(
        ...,
        description="HTML body for mail clients (bold section headers, lists)",
    )
    format_version: str = Field(
        ...,
        description="Template revision; must match app.preview.formatting.EMAIL_FORMAT_VERSION",
    )


class PreviewCreateResponse(BaseModel):
    """
    Full admin preview: pulse + fee + Doc/email shapes + printable doc block.
    Weekly Pulse N increments only on successful Create Preview.
    """

    email_template_version: str = Field(
        ...,
        description="Same as email.format_version — duplicated at root so clients can detect stale API without parsing nested email.",
    )
    weekly_pulse_n: int
    as_on: AsOnBlock
    pulse: PulseGenerateResponse
    doc_append: DocAppendPayload
    email: EmailPreview
    doc_block_plain: str
