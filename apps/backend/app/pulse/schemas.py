"""Pydantic models for LLM1 / LLM2 JSON and API responses."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.fee.schemas import FeeExplainerBlock


class ThemeItem(BaseModel):
    name: str
    volume_hint: str | None = None
    frequency_rank: int | None = None

    @field_validator("volume_hint", mode="before")
    @classmethod
    def coerce_volume_hint(cls, v: Any) -> str | None:
        # Groq often returns counts as integers; keep schema tolerant.
        if v is None:
            return None
        if isinstance(v, bool):
            return str(v).lower()
        if isinstance(v, (int, float)):
            return str(v)
        return str(v)

    @field_validator("frequency_rank", mode="before")
    @classmethod
    def coerce_frequency_rank(cls, v: Any) -> int | None:
        if v is None or v == "":
            return None
        if isinstance(v, int):
            return v
        if isinstance(v, str) and v.strip().isdigit():
            return int(v.strip())
        return v  # let pydantic error if invalid


class QuoteItem(BaseModel):
    theme: str
    quote: str
    review_id: str | None = None


class AnalysisJson(BaseModel):
    """LLM1 (Groq) — compact structured output."""

    themes: list[ThemeItem] = Field(default_factory=list, max_length=5)
    top_3_theme_names: list[str] = Field(min_length=3, max_length=3)
    quotes: list[QuoteItem] = Field(min_length=3, max_length=3)

    @field_validator("themes")
    @classmethod
    def at_most_five_themes(cls, v: list[ThemeItem]) -> list[ThemeItem]:
        return v[:5]


class PulseFinalJson(BaseModel):
    """LLM2 (Gemini) — final note + actions only."""

    weekly_note: str
    actions: list[str] = Field(min_length=3, max_length=3)


class PulseGenerateMeta(BaseModel):
    reviews_sampled: int
    groq_model: str
    gemini_model: str
    generated_at_iso: str
    note_word_count: int


class PulseGenerateResponse(BaseModel):
    """API payload: analysis + final copy + meta + optional fee explainer (Phase 4)."""

    analysis: AnalysisJson
    weekly_note: str
    actions: list[str]
    meta: PulseGenerateMeta
    fee: FeeExplainerBlock | None = None


class ErrorPayload(BaseModel):
    detail: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def count_words(text: str) -> int:
    return len((text or "").split())


def clamp_note_to_max_words(note: str, max_words: int = 250) -> tuple[str, bool]:
    """
    Enforce assignment cap; returns (trimmed, was_truncated).
    """
    words = (note or "").split()
    if len(words) <= max_words:
        return note.strip(), False
    return " ".join(words[:max_words]).rstrip() + "…", True
