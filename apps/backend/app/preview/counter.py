"""Persisted Weekly Pulse serial N (increment on each successful Create Preview)."""

from __future__ import annotations

import json
from pathlib import Path
from app.common.storage_mode import warn_if_ephemeral


def read_last_n(path: Path) -> int:
    if not path.is_file():
        return 0
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return int(raw.get("last_n", 0))
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return 0


def write_last_n(path: Path, n: int) -> None:
    warn_if_ephemeral("weekly_pulse_counter.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"last_n": n}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def increment_weekly_pulse_n(path: Path) -> int:
    """Return the new N after increment (starts at 1)."""
    n = read_last_n(path) + 1
    write_last_n(path, n)
    return n
