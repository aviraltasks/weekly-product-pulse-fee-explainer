"""Sidecar JSON for last fetch time, errors, and row counts."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from app.common.storage_mode import warn_if_ephemeral


@dataclass
class ReviewsMetadata:
    last_attempt_at_iso: str | None = None
    last_success_at_iso: str | None = None
    last_error: str | None = None
    row_count: int = 0
    last_added_count: int = 0
    last_fetched_count: int = 0
    last_duplicate_count: int = 0
    last_filtered_count: int = 0
    last_meaningful_count: int = 0
    last_decision: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_metadata(path: Path) -> ReviewsMetadata:
    if not path.is_file():
        return ReviewsMetadata()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return ReviewsMetadata(
            last_attempt_at_iso=raw.get("last_attempt_at_iso"),
            last_success_at_iso=raw.get("last_success_at_iso"),
            last_error=raw.get("last_error"),
            row_count=int(raw.get("row_count") or 0),
            last_added_count=int(raw.get("last_added_count") or 0),
            last_fetched_count=int(raw.get("last_fetched_count") or 0),
            last_duplicate_count=int(raw.get("last_duplicate_count") or 0),
            last_filtered_count=int(raw.get("last_filtered_count") or 0),
            last_meaningful_count=int(raw.get("last_meaningful_count") or 0),
            last_decision=raw.get("last_decision"),
        )
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return ReviewsMetadata()


def save_metadata(path: Path, meta: ReviewsMetadata) -> None:
    warn_if_ephemeral("reviews_metadata.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(meta.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
