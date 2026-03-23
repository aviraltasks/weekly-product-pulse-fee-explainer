"""Synchronous fetch from Google Play (google-play-scraper)."""

from __future__ import annotations

from typing import Any

from google_play_scraper import Sort, reviews


def fetch_reviews_sync(
    app_id: str,
    *,
    lang: str = "en",
    country: str = "in",
    max_count: int = 500,
) -> list[dict[str, Any]]:
    """
    Pull up to max_count reviews (paginates with continuation_token).
    """
    collected: list[dict[str, Any]] = []
    continuation_token = None
    remaining = max_count

    while remaining > 0:
        batch_n = min(200, remaining)
        batch, continuation_token = reviews(
            app_id,
            lang=lang,
            country=country,
            sort=Sort.NEWEST,
            count=batch_n,
            continuation_token=continuation_token,
        )
        if not batch:
            break
        collected.extend(batch)
        remaining = max_count - len(collected)
        if continuation_token is None:
            break

    return collected[:max_count]
