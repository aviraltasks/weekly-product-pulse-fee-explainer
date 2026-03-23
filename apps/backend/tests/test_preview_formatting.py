"""Preview formatting — As on, subject, Doc append fields, serialization."""

from __future__ import annotations

from app.fee.schemas import FeeExplainerBlock
from app.preview.formatting import (
    build_doc_append_payload,
    build_email_subject,
    format_as_on_display,
)
from app.preview.schemas import DocAppendPayload, PreviewCreateResponse
from app.pulse.schemas import AnalysisJson, PulseGenerateMeta, PulseGenerateResponse, QuoteItem, ThemeItem


def _sample_pulse(*, fee: FeeExplainerBlock | None = None) -> PulseGenerateResponse:
    analysis = AnalysisJson(
        themes=[
            ThemeItem(name="T1", volume_hint="12"),
            ThemeItem(name="T2", volume_hint="8"),
            ThemeItem(name="T3", volume_hint="5"),
        ],
        top_3_theme_names=["T1", "T2", "T3"],
        quotes=[
            QuoteItem(theme="T1", quote="Quote one is long enough for tests."),
            QuoteItem(theme="T2", quote="Quote two is long enough for tests."),
            QuoteItem(theme="T3", quote="Quote three is long enough for tests."),
        ],
    )
    meta = PulseGenerateMeta(
        reviews_sampled=3,
        groq_model="g",
        gemini_model="m",
        generated_at_iso="2025-01-01T00:00:00+00:00",
        note_word_count=10,
    )
    return PulseGenerateResponse(
        analysis=analysis,
        weekly_note="Weekly leadership note for tests.",
        actions=["a1", "a2", "a3"],
        meta=meta,
        fee=fee,
    )


def test_format_as_on_display_ist() -> None:
    d = format_as_on_display(iso_utc="2025-03-17T13:15:00+00:00", tz_name="Asia/Kolkata")
    assert "2025" in d or "Mar" in d
    assert "IST" in d


def test_email_subject_pattern() -> None:
    s = build_email_subject(as_on_display="17 Mar 2025, 18:45 IST", weekly_pulse_n=7)
    assert "Weekly Pulse + Fee Explainer" in s
    assert "As on 17 Mar 2025, 18:45 IST" in s
    assert "Weekly Pulse 7" in s


def test_doc_append_payload_with_fee() -> None:
    fee = FeeExplainerBlock(
        fee_scenario="Scenario",
        explanation_bullets=["b1"],
        source_links=["https://a.example", "https://b.example"],
        last_checked_iso="2025-01-01T00:00:00Z",
    )
    pulse = _sample_pulse(fee=fee)
    t = build_doc_append_payload(pulse=pulse, as_on_display="d1", fee=fee)
    doc = DocAppendPayload(
        date=t[0],
        weekly_pulse=t[1],
        fee_scenario=t[2],
        explanation_bullets=t[3],
        source_links=t[4],
        last_checked_iso=t[5],
    )
    assert doc.date == "d1"
    assert doc.weekly_pulse == pulse.weekly_note
    assert doc.fee_scenario == "Scenario"
    assert len(doc.source_links) == 2


def test_preview_create_response_json_roundtrip() -> None:
    pulse = _sample_pulse()
    p = PreviewCreateResponse(
        email_template_version="2",
        weekly_pulse_n=1,
        as_on={"iso_utc": "2025-01-01T00:00:00Z", "display": "1 Jan 2025, 00:00 IST"},
        pulse=pulse,
        doc_append=DocAppendPayload(
            date="d",
            weekly_pulse="w",
        ),
        email={
            "subject": "s",
            "body_plain": "b",
            "body_html": "<p>b</p>",
            "format_version": "2",
        },
        doc_block_plain="block",
    )
    dumped = p.model_dump(mode="json")
    assert dumped["email_template_version"] == "2"
    assert dumped["weekly_pulse_n"] == 1
    assert dumped["pulse"]["weekly_note"] == "Weekly leadership note for tests."
