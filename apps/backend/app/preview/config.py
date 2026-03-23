"""Preview package configuration (counter path, display timezone)."""

from __future__ import annotations

import os
from pathlib import Path


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_weekly_pulse_counter_path() -> Path:
    override = os.getenv("WEEKLY_PULSE_COUNTER_PATH")
    if override:
        return Path(override)
    return _backend_root() / "data" / "weekly_pulse_counter.json"


def get_preview_display_timezone() -> str:
    """IANA zone for 'As on — … IST' style line (default India)."""
    return os.getenv("PREVIEW_DISPLAY_TIMEZONE", "Asia/Kolkata").strip() or "Asia/Kolkata"
