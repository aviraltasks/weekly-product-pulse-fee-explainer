"""Orchestrate pulse generation + Weekly Pulse N + Doc/email shapes."""

from __future__ import annotations

from datetime import datetime, timezone

from app.preview.config import get_preview_display_timezone, get_weekly_pulse_counter_path
from app.preview.counter import increment_weekly_pulse_n
from app.preview.formatting import (
    EMAIL_FORMAT_VERSION,
    build_doc_append_payload,
    build_doc_block_plain,
    build_email_body_html,
    build_email_body_plain,
    build_email_subject,
    format_as_on_display,
)
from app.preview.schemas import AsOnBlock, DocAppendPayload, EmailPreview, PreviewCreateResponse
from app.pulse.pipeline import generate_pulse


async def create_preview() -> PreviewCreateResponse:
    """
    Run full pulse pipeline, then increment N and attach As on + Doc/email package.
    """
    pulse = await generate_pulse()
    now = datetime.now(timezone.utc)
    iso_utc = now.isoformat().replace("+00:00", "Z")

    tz = get_preview_display_timezone()
    as_on_display = format_as_on_display(iso_utc=iso_utc, tz_name=tz)

    n = increment_weekly_pulse_n(get_weekly_pulse_counter_path())
    fee = pulse.fee

    d_date, d_note, d_scen, d_bullets, d_links, d_last = build_doc_append_payload(
        pulse=pulse,
        as_on_display=as_on_display,
        fee=fee,
    )
    doc_append = DocAppendPayload(
        date=d_date,
        weekly_pulse=d_note,
        fee_scenario=d_scen,
        explanation_bullets=d_bullets,
        source_links=d_links,
        last_checked_iso=d_last,
        weekly_pulse_n=n,
    )

    doc_block_plain = build_doc_block_plain(
        pulse=pulse,
        weekly_pulse_n=n,
        as_on_display=as_on_display,
        fee=fee,
    )
    email = EmailPreview(
        subject=build_email_subject(as_on_display=as_on_display, weekly_pulse_n=n),
        body_plain=build_email_body_plain(
            pulse=pulse,
            fee=fee,
            as_on_display=as_on_display,
        ),
        body_html=build_email_body_html(
            pulse=pulse,
            fee=fee,
            as_on_display=as_on_display,
        ),
        format_version=EMAIL_FORMAT_VERSION,
    )

    return PreviewCreateResponse(
        email_template_version=EMAIL_FORMAT_VERSION,
        weekly_pulse_n=n,
        as_on=AsOnBlock(iso_utc=iso_utc, display=as_on_display),
        pulse=pulse,
        doc_append=doc_append,
        email=email,
        doc_block_plain=doc_block_plain,
    )
