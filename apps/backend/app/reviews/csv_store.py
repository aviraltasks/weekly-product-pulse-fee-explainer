"""Append / merge reviews into reviews_master.csv with stable schema."""

from __future__ import annotations

import csv
import os
import tempfile
from pathlib import Path
from typing import Any
from app.common.storage_mode import warn_if_ephemeral

FIELDNAMES: tuple[str, ...] = (
    "review_id",
    "user_name",
    "content",
    "score",
    "review_created_version",
    "at_iso",
    "thumbs_up",
    "reply_content",
    "replied_at_iso",
    "app_version",
    "fetched_at_iso",
)


def _row_key(row: dict[str, Any]) -> str:
    return str(row.get("review_id", "")).strip()


def read_reviews_by_id(csv_path: Path) -> dict[str, dict[str, Any]]:
    """Load CSV into a dict keyed by review_id (last write wins if dupes in file)."""
    if not csv_path.is_file():
        return {}
    out: dict[str, dict[str, Any]] = {}
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            if not raw:
                continue
            row = {k: (v if v is not None else "") for k, v in raw.items()}
            kid = _row_key(row)
            if kid:
                out[kid] = row
    return out


def read_review_ids(csv_path: Path) -> set[str]:
    """Load just review IDs for fast duplicate checks during fetch."""
    return set(read_reviews_by_id(csv_path).keys())


def write_reviews_atomic(csv_path: Path, rows: list[dict[str, Any]]) -> None:
    """Write all rows; atomic replace via temp file in same directory."""
    warn_if_ephemeral("reviews_master.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rows_sorted = sorted(rows, key=lambda r: (r.get("at_iso") or "", r.get("review_id") or ""))
    fd, tmp = tempfile.mkstemp(
        suffix=".csv",
        dir=csv_path.parent,
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(FIELDNAMES), extrasaction="ignore")
            w.writeheader()
            for row in rows_sorted:
                w.writerow({k: row.get(k, "") for k in FIELDNAMES})
        os.replace(tmp, csv_path)
    finally:
        if os.path.isfile(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


def merge_new_reviews(
    csv_path: Path,
    new_rows: list[dict[str, Any]],
) -> tuple[int, int, int]:
    """
    Merge new_rows into existing CSV by review_id.
    Returns (previous_count, added_count, total_count).
    """
    existing = read_reviews_by_id(csv_path)
    before = len(existing)
    added = 0
    for row in new_rows:
        kid = _row_key(row)
        if not kid:
            continue
        if kid not in existing:
            added += 1
        existing[kid] = row
    total = len(existing)
    write_reviews_atomic(csv_path, list(existing.values()))
    return before, added, total
