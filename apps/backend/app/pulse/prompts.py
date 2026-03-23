"""LLM prompts — LLM2 must never see raw reviews, only structured analysis JSON."""

from __future__ import annotations

import json
from typing import Any

GROQ_SYSTEM = """You are a product analyst. Given Play Store reviews (compressed), output ONLY valid JSON.
Rules:
- Cluster into at most 5 themes; identify the TOP 3 themes by volume/frequency.
- For each of the top 3 themes, pick ONE short quote: verbatim (or minimal trim) from a real review in that theme. Do not invent quotes.
- Output JSON keys: themes (array of {name, volume_hint?, frequency_rank?}), top_3_theme_names (exactly 3 strings), quotes (exactly 3 objects {theme, quote, review_id?}).
- themes[].name should align with top_3_theme_names where possible.
- No PII beyond what is in reviews; no prose outside JSON."""


def build_groq_user_payload(samples: list[dict[str, str]]) -> str:
    """Compact JSON batch for Groq."""
    payload: dict[str, Any] = {
        "instruction": "Analyze these user reviews for INDmoney (in.indwealth).",
        "reviews": samples,
    }
    return json.dumps(payload, ensure_ascii=False)


GEMINI_SYSTEM_PREFIX = """You are an executive product communications assistant.
Write a leadership-style weekly note and 3 one-line actions.
Target about 120-150 words for the note; hard maximum 250 words. Neutral, no PII.
Return ONLY valid JSON with keys: weekly_note (string), actions (array of exactly 3 short strings).
Do not include markdown fences."""


def build_gemini_user_prompt(analysis_dict: dict[str, Any]) -> str:
    """LLM2 input = LLM1 JSON only + instructions (no raw reviews)."""
    body = json.dumps(analysis_dict, ensure_ascii=False)
    return (
        f"{GEMINI_SYSTEM_PREFIX}\n\n"
        "Structured analysis from prior step (do not question its facts; synthesize):\n"
        f"{body}\n\n"
        "Produce JSON only."
    )
