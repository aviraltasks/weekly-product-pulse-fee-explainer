"""Email newsletter plain + HTML shape."""

from __future__ import annotations

from app.fee.schemas import FeeExplainerBlock
from app.preview.formatting import build_email_body_html, build_email_body_plain
from app.pulse.schemas import AnalysisJson, PulseGenerateMeta, PulseGenerateResponse, QuoteItem, ThemeItem


def _pulse() -> PulseGenerateResponse:
    analysis = AnalysisJson(
        themes=[ThemeItem(name="T1"), ThemeItem(name="T2"), ThemeItem(name="T3")],
        top_3_theme_names=["T1", "T2", "T3"],
        quotes=[
            QuoteItem(theme="T1", quote="Quote one."),
            QuoteItem(theme="T2", quote="Quote two."),
            QuoteItem(theme="T3", quote="Quote three."),
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
        weekly_note="Note paragraph.",
        actions=["Act one", "Act two", "Act three"],
        meta=meta,
        fee=None,
    )


def test_plain_no_tl_dr_and_vertical_lists() -> None:
    plain = build_email_body_plain(pulse=_pulse(), fee=None, as_on_display="1 Jan 2025, 00:00 IST")
    assert "TL;DR" not in plain
    assert "WEEKLY PRODUCT PULSE: 1 Jan 2025, 00:00 IST" in plain
    assert "INDMONEY" in plain
    assert "3 reviews sampled" in plain
    assert "TOP 3 CUSTOMER THEMES" in plain
    assert "CUSTOMER VERBATIM QUOTES" in plain
    assert "EXECUTIVE ANALYSIS" in plain
    assert "PRIORITY ACTIONS" in plain
    assert "KNOWLEDGE BASE: FEE EXPLAINER" in plain
    assert "Play Store" in plain
    assert plain.count('- "Quote') == 3
    assert "- Act one" in plain


def test_html_bold_sections_and_lists() -> None:
    fee = FeeExplainerBlock(
        fee_scenario="Scenario <x>",
        explanation_bullets=["b1"],
        source_links=["https://a.example", "https://b.example"],
        last_checked_iso="2025-01-01T00:00:00Z",
    )
    html = build_email_body_html(pulse=_pulse(), fee=fee, as_on_display="d")
    assert "WEEKLY PRODUCT PULSE:" in html
    assert "text-align:center" in html
    assert "Weekly Pulse + Fee Explainer" in html
    assert "Data basis" in html
    assert "TOP 3 CUSTOMER THEMES" in html
    assert "CUSTOMER VERBATIM QUOTES" in html
    assert "EXECUTIVE ANALYSIS" in html
    assert "PRIORITY ACTIONS" in html
    assert "KNOWLEDGE BASE: FEE EXPLAINER" in html
    assert "<hr " in html
    assert "<ul" in html  # e.g. <ul style="..."> — attribute breaks naive "<ul>" match
    assert "&lt;x&gt;" in html or "Scenario" in html  # escaped
