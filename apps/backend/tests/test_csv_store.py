"""CSV merge idempotency and atomic write behavior."""

from __future__ import annotations

from pathlib import Path

from app.reviews import csv_store


def _row(rid: str, content: str, at: str = "2025-01-01T00:00:00+00:00") -> dict[str, str]:
    return {
        "review_id": rid,
        "user_name": "u",
        "content": content,
        "score": "5",
        "review_created_version": "",
        "at_iso": at,
        "thumbs_up": "0",
        "reply_content": "",
        "replied_at_iso": "",
        "app_version": "",
        "fetched_at_iso": "2025-01-02T00:00:00+00:00",
    }


def test_merge_idempotent_same_id_updates(tmp_path: Path) -> None:
    p = tmp_path / "reviews_master.csv"
    before, added, total = csv_store.merge_new_reviews(p, [_row("a", "first version long enough")])
    assert before == 0 and added == 1 and total == 1

    before2, added2, total2 = csv_store.merge_new_reviews(
        p,
        [_row("a", "second version replaces content long enough")],
    )
    assert before2 == 1 and added2 == 0 and total2 == 1
    by_id = csv_store.read_reviews_by_id(p)
    assert by_id["a"]["content"] == "second version replaces content long enough"


def test_merge_accumulates_distinct_ids(tmp_path: Path) -> None:
    p = tmp_path / "reviews_master.csv"
    _, _, total = csv_store.merge_new_reviews(
        p,
        [
            _row("x", "one review text here ok", "2025-01-01T00:00:00+00:00"),
            _row("y", "two review text here ok", "2025-01-02T00:00:00+00:00"),
        ],
    )
    assert total == 2
    again_before, again_added, again_total = csv_store.merge_new_reviews(p, [_row("x", "updated x text here ok")])
    assert again_before == 2 and again_added == 0 and again_total == 2
