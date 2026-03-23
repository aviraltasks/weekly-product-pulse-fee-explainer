"""Unit tests for review normalization / filtering."""

from __future__ import annotations

from datetime import datetime, timezone

from app.reviews.clean import is_meaningful_content, normalize_scraped_review


def test_normalize_drops_short_content() -> None:
    raw = {
        "reviewId": "id1",
        "userName": "a",
        "content": "short",
        "score": 5,
        "at": datetime.now(timezone.utc),
    }
    assert normalize_scraped_review(raw, fetched_at_iso="2025-01-01T00:00:00+00:00", min_content_length=10) is None


def test_normalize_keeps_valid_row() -> None:
    at = datetime(2025, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
    raw = {
        "reviewId": "rid-99",
        "userName": " Test User ",
        "content": "This is a long enough review for the pipeline.",
        "score": 4,
        "reviewCreatedVersion": "1.0",
        "at": at,
        "thumbsUpCount": 3,
        "replyContent": "Thanks",
        "repliedAt": at,
        "appVersion": "2.1",
    }
    out = normalize_scraped_review(
        raw,
        fetched_at_iso="2025-03-02T00:00:00+00:00",
        min_content_length=10,
    )
    assert out is not None
    assert out["review_id"] == "rid-99"
    assert out["user_name"] == "Test User"
    assert out["score"] == "4"
    assert "2025-03-01" in out["at_iso"]
    assert out["fetched_at_iso"] == "2025-03-02T00:00:00+00:00"


def test_meaningful_content_rejects_emoji_noise() -> None:
    assert (
        is_meaningful_content(
            "Super app 😊 very helpful for tracking investments",
            min_content_length=10,
            min_word_count=3,
        )
        is False
    )


def test_meaningful_content_rejects_alphanumeric_gibberish() -> None:
    assert (
        is_meaningful_content(
            "a1 b2 c3 d4 e5 f6",
            min_content_length=10,
            min_word_count=3,
        )
        is False
    )
