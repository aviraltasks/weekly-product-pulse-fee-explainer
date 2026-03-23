"""Sample + truncate reviews from reviews_master.csv for LLM1."""

from __future__ import annotations

from pathlib import Path

from app.reviews import clean, config as reviews_config
from app.reviews import csv_store


def load_sample_for_pulse(
    csv_path: Path,
    *,
    max_reviews: int,
    truncate_chars: int,
) -> list[dict[str, str]]:
    """
    Newest-first (by at_iso), dedupe near-identical content, truncate body.
    """
    by_id = csv_store.read_reviews_by_id(csv_path)
    rows = list(by_id.values())
    rows.sort(key=lambda r: r.get("at_iso") or "", reverse=True)

    out: list[dict[str, str]] = []
    seen_prefix: set[str] = set()
    min_len = reviews_config.get_min_review_length()
    min_words = reviews_config.get_min_meaningful_words()

    for r in rows:
        if len(out) >= max_reviews:
            break
        content = (r.get("content") or "").strip()
        if not clean.is_meaningful_content(
            content,
            min_content_length=min_len,
            min_word_count=min_words,
        ):
            continue
        if len(content) > truncate_chars:
            content = content[:truncate_chars].rstrip() + "…"
        key = content[:96].lower()
        if key in seen_prefix:
            continue
        seen_prefix.add(key)
        rid = str(r.get("review_id") or "").strip()
        out.append(
            {
                "review_id": rid,
                "content": content,
                "score": str(r.get("score") or ""),
            }
        )
    return out
