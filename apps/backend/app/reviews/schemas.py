"""Pydantic models for reviews API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReviewsStatusResponse(BaseModel):
    """Admin status: last refresh + counts (+ optional error)."""

    review_count: int = Field(..., description="Rows in reviews_master.csv (unique review_id)")
    last_attempt_at_iso: str | None = None
    last_success_at_iso: str | None = None
    last_error: str | None = None
    last_added_count: int = 0
    last_fetched_count: int = 0
    last_duplicate_count: int = 0
    last_filtered_count: int = 0
    last_meaningful_count: int = 0
    last_decision: str | None = None
    play_store_app_id: str = Field(..., description="Configured Google Play package id")
    scheduler_enabled: bool = True
    fetch_interval_hours: int = 48


class FetchTriggerResponse(BaseModel):
    """Result of a manual or scheduled fetch."""

    ok: bool
    review_count: int
    last_success_at_iso: str | None = None
    last_error: str | None = None
    last_added_count: int = 0
    last_fetched_count: int = 0
    last_duplicate_count: int = 0
    last_filtered_count: int = 0
    last_meaningful_count: int = 0
    last_decision: str | None = None


class ReviewsDecisionResponse(BaseModel):
    """Decision summary for whether a new pulse run is recommended."""

    decision: str | None = None
    meaningful_new_reviews: int = 0
    min_meaningful_for_pulse: int = 0
    should_run_pulse: bool = False
    fetched_count: int = 0
    duplicate_count: int = 0
    filtered_count: int = 0
    last_success_at_iso: str | None = None
    last_error: str | None = None
