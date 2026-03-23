"""Build As on line, Doc block text, email subject/body from pulse + fee."""

from __future__ import annotations

# Bump when section labels / HTML layout in build_email_body_* changes (for health + API clients).
EMAIL_FORMAT_VERSION = "2"

import html
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.fee.schemas import FeeExplainerBlock
from app.pulse.schemas import AnalysisJson, PulseGenerateResponse


def format_as_on_display(*, iso_utc: str, tz_name: str) -> str:
    """e.g. 17 Mar 2025, 18:45 IST"""
    try:
        dt = datetime.fromisoformat(iso_utc.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    except ValueError:
        dt = datetime.now(timezone.utc)
    local = dt.astimezone(ZoneInfo(tz_name))
    return local.strftime("%d %b %Y, %H:%M") + " IST"


def _theme_volume_line(analysis: AnalysisJson) -> str:
    names = analysis.top_3_theme_names
    parts = []
    for i, name in enumerate(names, start=1):
        hint = None
        for t in analysis.themes:
            if t.name.strip().lower() == name.strip().lower():
                hint = t.volume_hint
                break
        if hint:
            parts.append(f"{i}) {name} ({hint})")
        else:
            parts.append(f"{i}) {name}")
    return "\n".join(parts)


def build_doc_block_plain(
    *,
    pulse: PulseGenerateResponse,
    weekly_pulse_n: int,
    as_on_display: str,
    fee: FeeExplainerBlock | None,
) -> str:
    """Printable block (newest-on-top style header) for Doc / preview pane."""
    a = pulse.analysis
    lines: list[str] = [
        "════════════════════════════════════════════════════════════",
        f"Weekly Pulse {weekly_pulse_n} · As on — {as_on_display}",
        "════════════════════════════════════════════════════════════",
        "",
        "PULSE (TL;DR)",
        f"Top themes this window: {', '.join(a.top_3_theme_names)}.",
        "",
        "TOP 3 THEMES (by volume)",
        _theme_volume_line(a),
        "",
        "EVIDENCE (1 quote / theme — verbatim)",
    ]
    for q in a.quotes:
        lines.append(f"• {q.theme}: \"{q.quote}\"")
    lines.extend(
        [
            "",
            "NOTE",
            pulse.weekly_note,
            "",
            "ACTIONS (3 — one line each)",
        ]
    )
    for i, act in enumerate(pulse.actions, start=1):
        lines.append(f"{i}) {act}")

    lines.extend(
        [
            "",
            "────────────────────────────────────────────────────────────",
            "FEE — " + (fee.fee_scenario if fee else "—"),
            "────────────────────────────────────────────────────────────",
        ]
    )
    if fee:
        for b in fee.explanation_bullets:
            lines.append(f"• {b}")
        src = " · ".join(fee.source_links) if fee.source_links else ""
        lines.append(f"Sources: {src}   |   Last checked: {fee.last_checked_iso}")
    else:
        lines.append("• Fee explainer not configured (set fee source URLs).")

    return "\n".join(lines)


def build_email_subject(*, as_on_display: str, weekly_pulse_n: int) -> str:
    return (
        f"Weekly Pulse + Fee Explainer — As on {as_on_display} — "
        f"Weekly Pulse {weekly_pulse_n}"
    )


def _email_intro_plain(*, reviews_sampled: int) -> str:
    """Static copy so readers know source, audience, and purpose (no extra LLM)."""
    return (
        "INDMONEY — WEEKLY PULSE + FEE EXPLAINER\n"
        "What this is: Themes and quotes from Google Play store reviews, a short leadership-style "
        "summary, suggested actions, plus a standardized exit-load explainer for context.\n"
        "Who it is for: Internal product / leadership (FYI; your teams assign owners).\n"
        f"Data basis: {reviews_sampled} reviews sampled for this pulse (see app config for window).\n"
    )


def _plain_section_rule() -> str:
    """Visual break between pulse content and fee reference (plain-text email)."""
    return "\n" + "─" * 56 + "\n"


def build_email_body_plain(
    *,
    pulse: PulseGenerateResponse,
    fee: FeeExplainerBlock | None,
    as_on_display: str,
) -> str:
    """Readable plain-text newsletter (no TL;DR; vertical bullets for quotes & actions)."""
    title_line = f"WEEKLY PRODUCT PULSE: {as_on_display}"
    intro = _email_intro_plain(reviews_sampled=pulse.meta.reviews_sampled)
    a = pulse.analysis
    top = " · ".join(f"({i}) {n}" for i, n in enumerate(a.top_3_theme_names, start=1))

    quote_lines = []
    for q in a.quotes:
        t = q.quote.strip()
        quote_lines.append(f'- "{t}"')

    action_lines = [f"- {act.strip()}" for act in pulse.actions]

    fee_block = ""
    if fee:
        fbullets = "\n".join(f"• {b}" for b in fee.explanation_bullets)
        src = " ".join(fee.source_links)
        fee_block = (
            _plain_section_rule()
            + "\n"
            "KNOWLEDGE BASE: FEE EXPLAINER — EXIT LOAD (reference only; not a fee or policy change)\n"
            f"Scenario: {fee.fee_scenario}\n\n"
            f"{fbullets}\n\n"
            f"Sources: {src} · Last checked: {fee.last_checked_iso}"
        )
    else:
        fee_block = (
            _plain_section_rule()
            + "\n"
            "KNOWLEDGE BASE: FEE EXPLAINER — EXIT LOAD (not configured)\n"
        )

    quotes_txt = "\n".join(quote_lines)
    actions_txt = "\n".join(action_lines)

    # Double-spacing between major sections for scanability
    return (
        f"{title_line}\n\n"
        f"{intro}\n"
        "TOP 3 CUSTOMER THEMES (by volume among sampled reviews)\n"
        f"{top}\n\n"
        "CUSTOMER VERBATIM QUOTES (Play Store excerpts; one per top theme)\n"
        f"{quotes_txt}\n\n"
        "EXECUTIVE ANALYSIS (AI-assisted leadership summary — not legal, tax, or investment advice)\n"
        f"{pulse.weekly_note}\n\n"
        "PRIORITY ACTIONS (suggested next steps — assign owners and timelines in your teams)\n"
        f"{actions_txt}"
        f"{fee_block}\n\n"
        f"As on — {as_on_display}\n"
        "— Not investment advice. Review themes may not reflect all users."
    )


def _email_intro_html(*, reviews_sampled: int) -> str:
    n = html.escape(str(reviews_sampled))
    return f"""<div style="background:#f5f5f5;padding:12px 14px;border-radius:6px;margin-bottom:28px;font-size:13px;color:#333;">
<p style="margin:0 0 8px 0;"><strong>INDMONEY — Weekly Pulse + Fee Explainer</strong></p>
<p style="margin:0 0 6px 0;"><strong>What this is:</strong> Themes and quotes from Google Play reviews, a short leadership-style summary, suggested actions, plus a standardized exit-load explainer for context.</p>
<p style="margin:0 0 6px 0;"><strong>Who it is for:</strong> Internal product / leadership (FYI; your teams assign owners).</p>
<p style="margin:0;"><strong>Data basis:</strong> {n} reviews sampled for this pulse (see app config for window).</p>
</div>"""


def _email_title_html(*, as_on_display: str) -> str:
    """Bold, centered document title for HTML email clients."""
    d = html.escape(as_on_display)
    return f"""<div style="text-align:center;margin:0 0 28px 0;padding:0 8px;">
<p style="margin:0;font-size:17px;font-weight:700;letter-spacing:0.06em;color:#111;line-height:1.35;">
WEEKLY PRODUCT PULSE: {d}
</p>
</div>"""


def build_email_body_html(
    *,
    pulse: PulseGenerateResponse,
    fee: FeeExplainerBlock | None,
    as_on_display: str,
) -> str:
    """HTML newsletter: bold section labels, lists for quotes & actions; user content escaped."""
    doc_title = _email_title_html(as_on_display=as_on_display)
    intro = _email_intro_html(reviews_sampled=pulse.meta.reviews_sampled)
    a = pulse.analysis
    top = " · ".join(f"({i}) {n}" for i, n in enumerate(a.top_3_theme_names, start=1))

    quote_items = "".join(
        f"<li>{html.escape(q.quote.strip())}</li>" for q in a.quotes
    )
    action_items = "".join(f"<li>{html.escape(act.strip())}</li>" for act in pulse.actions)

    note_safe = html.escape(pulse.weekly_note)
    note_html = "<p>" + note_safe.replace("\n", "<br>\n") + "</p>"

    sec = 'margin:0 0 28px 0;'
    lbl = 'margin:0 0 10px 0;font-size:13px;letter-spacing:0.02em;color:#111;'

    if fee:
        fee_title = html.escape(fee.fee_scenario)
        fee_bullets = "".join(f"<li>{html.escape(b)}</li>" for b in fee.explanation_bullets)
        src_links = " ".join(
            f'<a href="{html.escape(u)}">{html.escape(u)}</a>' for u in fee.source_links
        )
        fee_section = (
            f'<hr style="border:none;border-top:1px solid #ccc;margin:32px 0 28px 0;" />'
            f'<div style="{sec}">'
            '<p style="' + lbl + '">'
            "<strong>KNOWLEDGE BASE: FEE EXPLAINER</strong> — Exit load "
            "(reference only; not a fee or policy change)</p>"
            f"<p style=\"margin:0 0 8px 0;\">Scenario: {fee_title}</p>"
            f"<ul style=\"margin:0 0 12px 0;padding-left:1.25em;\">{fee_bullets}</ul>"
            f"<p style=\"margin:0;color:#444;font-size:13px;\">Sources: {src_links} · "
            f"Last checked: {html.escape(fee.last_checked_iso)}</p>"
            "</div>"
        )
    else:
        fee_section = (
            '<hr style="border:none;border-top:1px solid #ccc;margin:32px 0 28px 0;" />'
            f'<div style="{sec}">'
            '<p style="' + lbl + '">'
            "<strong>KNOWLEDGE BASE: FEE EXPLAINER</strong> — Exit load (not configured)</p>"
            "</div>"
        )

    as_on_esc = html.escape(as_on_display)

    # Placeholder avoids f-string interpreting `{` / `}` if they appear in weekly_note HTML.
    _note_slot = "\x00EMAIL_NOTE_BODY\x00"
    body = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="font-family: Arial, Helvetica, sans-serif; font-size: 14px; line-height: 1.6; color: #222;">
{doc_title}
{intro}
<div style="{sec}">
<p style="{lbl}"><strong>TOP 3 CUSTOMER THEMES</strong> (by volume among sampled reviews)</p>
<p style="margin:0;">{html.escape(top)}</p>
</div>
<div style="{sec}">
<p style="{lbl}"><strong>CUSTOMER VERBATIM QUOTES</strong> (Play Store excerpts; one per top theme)</p>
<ul style="margin:0;padding-left:1.25em;">{quote_items}</ul>
</div>
<div style="{sec}">
<p style="{lbl}"><strong>EXECUTIVE ANALYSIS</strong> (AI-assisted leadership summary — not legal, tax, or investment advice)</p>
{_note_slot}
</div>
<div style="margin:0 0 28px 0;">
<p style="{lbl}"><strong>PRIORITY ACTIONS</strong> (suggested next steps — assign owners and timelines in your teams)</p>
<ul style="margin:0;padding-left:1.25em;">{action_items}</ul>
</div>
{fee_section}
<p style="margin-top:28px;color:#555;"><em>As on — {as_on_esc}</em></p>
<p style="color:#555;font-size:12px;"><em>— Not investment advice. Review themes may not reflect all users.</em></p>
</body></html>"""
    return body.replace(_note_slot, note_html)


def build_doc_append_payload(
    *,
    pulse: PulseGenerateResponse,
    as_on_display: str,
    fee: FeeExplainerBlock | None,
) -> tuple[str, str, str, list[str], list[str], str]:
    """Returns fields for DocAppendPayload."""
    if fee:
        return (
            as_on_display,
            pulse.weekly_note,
            fee.fee_scenario,
            list(fee.explanation_bullets),
            list(fee.source_links),
            fee.last_checked_iso,
        )
    return as_on_display, pulse.weekly_note, "", [], [], ""
