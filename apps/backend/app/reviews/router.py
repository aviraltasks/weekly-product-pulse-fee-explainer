"""HTTP routes for reviews status and manual fetch."""

from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Response

from app.reviews import config, csv_store, metadata, service
from app.reviews.schemas import FetchTriggerResponse, ReviewsDecisionResponse, ReviewsStatusResponse

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("/status", response_model=ReviewsStatusResponse)
def get_reviews_status() -> ReviewsStatusResponse:
    meta = metadata.load_metadata(config.get_metadata_path())
    csv_path = config.get_csv_path()
    n = len(csv_store.read_reviews_by_id(csv_path))
    return ReviewsStatusResponse(
        review_count=n,
        last_attempt_at_iso=meta.last_attempt_at_iso,
        last_success_at_iso=meta.last_success_at_iso,
        last_error=meta.last_error,
        last_added_count=meta.last_added_count,
        last_fetched_count=meta.last_fetched_count,
        last_duplicate_count=meta.last_duplicate_count,
        last_filtered_count=meta.last_filtered_count,
        last_meaningful_count=meta.last_meaningful_count,
        last_decision=meta.last_decision,
        play_store_app_id=config.get_play_store_app_id(),
        scheduler_enabled=config.scheduler_enabled(),
        fetch_interval_hours=config.fetch_interval_hours(),
    )


@router.post("/fetch", response_model=FetchTriggerResponse)
async def post_reviews_fetch(
    x_cron_token: str | None = Header(default=None, alias="X-Cron-Token"),
) -> FetchTriggerResponse:
    """Trigger a Play Store fetch → merge into CSV (same path as scheduler)."""
    expected = config.get_fetch_trigger_token()
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="Fetch trigger is not configured: set CRON_TRIGGER_TOKEN.",
        )
    if (x_cron_token or "").strip() != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Cron-Token")

    meta = await service.run_fetch_cycle()
    csv_path = config.get_csv_path()
    n = len(csv_store.read_reviews_by_id(csv_path))
    return FetchTriggerResponse(
        ok=meta.last_error is None,
        review_count=n,
        last_success_at_iso=meta.last_success_at_iso,
        last_error=meta.last_error,
        last_added_count=meta.last_added_count,
        last_fetched_count=meta.last_fetched_count,
        last_duplicate_count=meta.last_duplicate_count,
        last_filtered_count=meta.last_filtered_count,
        last_meaningful_count=meta.last_meaningful_count,
        last_decision=meta.last_decision,
    )


@router.get("/quotes-export")
def get_reviews_quotes_export() -> Response:
    """Download CSV: feedback_id, feedback_date, quote_text (no reviewer names)."""
    csv_path = config.get_csv_path()
    data = csv_store.build_quotes_export_csv_bytes(csv_path)
    return Response(
        content=data,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="review_quotes_export.csv"',
            "Cache-Control": "no-store",
        },
    )


@router.get("/decision", response_model=ReviewsDecisionResponse)
def get_reviews_decision() -> ReviewsDecisionResponse:
    """Small decision endpoint for admin UI badges / quick checks."""
    meta = metadata.load_metadata(config.get_metadata_path())
    threshold = config.get_min_meaningful_for_pulse()
    decision = meta.last_decision
    should_run = decision == "run_ready" and meta.last_error is None
    return ReviewsDecisionResponse(
        decision=decision,
        meaningful_new_reviews=meta.last_meaningful_count,
        min_meaningful_for_pulse=threshold,
        should_run_pulse=should_run,
        fetched_count=meta.last_fetched_count,
        duplicate_count=meta.last_duplicate_count,
        filtered_count=meta.last_filtered_count,
        last_success_at_iso=meta.last_success_at_iso,
        last_error=meta.last_error,
    )
