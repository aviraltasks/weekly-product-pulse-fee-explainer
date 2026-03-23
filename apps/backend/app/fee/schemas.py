"""Fee explainer DTO (matches MCP doc-append shape)."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class FeeExplainerBlock(BaseModel):
    """≤6 bullets, 2 official links, last checked — neutral tone."""

    fee_scenario: str = Field(..., description="Title line, e.g. fund + exit load")
    explanation_bullets: list[str] = Field(default_factory=list, max_length=6)
    source_links: list[str] = Field(default_factory=list, min_length=2, max_length=2)
    last_checked_iso: str = Field(..., description="UTC ISO timestamp of last refresh")

    @field_validator("explanation_bullets", mode="before")
    @classmethod
    def cap_bullets(cls, v: list[str]) -> list[str]:
        if not v:
            return []
        return [str(x).strip() for x in v if str(x).strip()][:6]


class FeeCachePayload(BaseModel):
    """Serialized cache + optional scrape excerpts."""

    fee_scenario: str
    explanation_bullets: list[str]
    source_links: list[str]
    last_checked_iso: str
    excerpts: dict[str, str] = Field(default_factory=dict)
