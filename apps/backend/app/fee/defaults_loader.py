"""Load fee scenario, Source 2 hardcoded bullets, and Source 1 placeholder."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.fee.config import get_fee_defaults_path, get_fee_source2_hardcoded_path


def load_fee_scenario() -> str:
    path = get_fee_defaults_path()
    if not path.is_file():
        return "INDmoney · SBI Large Cap · Exit load"
    raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    title = str(raw.get("fee_scenario") or raw.get("fee_scenario_title") or "").strip()
    return title or "INDmoney · SBI Large Cap · Exit load"


def load_source1_placeholder() -> str:
    path = get_fee_defaults_path()
    if not path.is_file():
        return (
            "Exit-load details for this fund load from INDmoney (Source 1) after refresh."
        )
    raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    ph = str(raw.get("source1_placeholder_bullet") or "").strip()
    if ph:
        return ph
    return (
        "Exit-load details for this fund load from INDmoney (Source 1) after refresh."
    )


def load_source2_hardcoded_bullets() -> list[str]:
    """SEBI 'How does exit load work?' — summarized, no network (see fee_source2_hardcoded.json)."""
    path = get_fee_source2_hardcoded_path()
    if not path.is_file():
        return []
    raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    bullets = raw.get("bullets") or []
    if not isinstance(bullets, list):
        return []
    return [str(b).strip() for b in bullets if str(b).strip()]


def build_explanation_bullets(indmoney_faq_paragraph: str | None) -> list[str]:
    """
    One bullet from Source 1 (INDmoney FAQ scrape or placeholder) + Source 2 hardcoded bullets.
    Total capped at 6 in FeeExplainerBlock.
    """
    s1 = (indmoney_faq_paragraph or "").strip() or load_source1_placeholder()
    s2 = load_source2_hardcoded_bullets()
    merged = [s1] + s2
    return merged[:6]


def load_fee_defaults() -> tuple[str, list[str]]:
    """Backward-compatible: title + bullets with no Source 1 scrape (placeholder + Source 2)."""
    return load_fee_scenario(), build_explanation_bullets(None)
