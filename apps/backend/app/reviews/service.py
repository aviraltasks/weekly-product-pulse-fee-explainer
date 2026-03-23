"""Orchestrate fetch → clean → CSV merge → metadata."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from app.reviews import clean, config, csv_store, metadata, play_fetch

logger = logging.getLogger(__name__)


async def run_fetch_cycle() -> metadata.ReviewsMetadata:
    """
    One fetch run (scheduler + manual POST use this).
    Updates metadata with attempt time; success updates row counts.
    """
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    meta_path = config.get_metadata_path()
    csv_path = config.get_csv_path()
    min_len = config.get_min_review_length()
    min_words = config.get_min_meaningful_words()
    min_meaningful_for_pulse = config.get_min_meaningful_for_pulse()

    meta = metadata.load_metadata(meta_path)
    meta.last_attempt_at_iso = now_iso
    meta.last_error = None
    meta.last_decision = None
    metadata.save_metadata(meta_path, meta)

    try:
        raw_rows = await asyncio.to_thread(
            play_fetch.fetch_reviews_sync,
            config.get_play_store_app_id(),
            lang=config.get_play_lang(),
            country=config.get_play_country(),
            max_count=config.get_fetch_max_reviews(),
        )
    except Exception as e:
        logger.exception("Play Store fetch failed")
        err = f"{type(e).__name__}: {e}"
        meta = metadata.load_metadata(meta_path)
        meta.last_attempt_at_iso = now_iso
        meta.last_error = err
        meta.last_fetched_count = 0
        meta.last_duplicate_count = 0
        meta.last_filtered_count = 0
        meta.last_meaningful_count = 0
        meta.last_decision = "fetch_error"
        metadata.save_metadata(meta_path, meta)
        return meta

    fetched_iso = now_iso
    normalized: list[dict[str, str]] = []
    existing_ids = csv_store.read_review_ids(csv_path)
    batch_seen: set[str] = set()
    duplicate_count = 0
    filtered_count = 0
    for raw in raw_rows:
        rid = str(raw.get("reviewId") or "").strip()
        if not rid or rid in existing_ids or rid in batch_seen:
            duplicate_count += 1
            continue
        batch_seen.add(rid)
        row = clean.normalize_scraped_review(
            raw,
            fetched_at_iso=fetched_iso,
            min_content_length=min_len,
            min_word_count=min_words,
        )
        if row:
            normalized.append(row)
        else:
            filtered_count += 1

    before, added, total = csv_store.merge_new_reviews(csv_path, normalized)
    if added == 0:
        decision = "skip_no_new"
    elif added < min_meaningful_for_pulse:
        decision = "skip_low_signal"
    else:
        decision = "run_ready"

    meta = metadata.ReviewsMetadata(
        last_attempt_at_iso=now_iso,
        last_success_at_iso=now_iso,
        last_error=None,
        row_count=total,
        last_added_count=added,
        last_fetched_count=len(raw_rows),
        last_duplicate_count=duplicate_count,
        last_filtered_count=filtered_count,
        last_meaningful_count=added,
        last_decision=decision,
    )
    metadata.save_metadata(meta_path, meta)
    logger.info(
        "Reviews fetch OK: before=%s fetched=%s duplicates=%s filtered=%s added=%s total=%s decision=%s",
        before,
        len(raw_rows),
        duplicate_count,
        filtered_count,
        added,
        total,
        decision,
    )
    return meta
