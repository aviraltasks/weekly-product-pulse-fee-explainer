"""Reviews module configuration (env-driven; lazy reads for tests)."""

from __future__ import annotations

import os
from pathlib import Path


def _backend_root() -> Path:
    # app/reviews/config.py -> parents[2] == apps/backend
    return Path(__file__).resolve().parents[2]


def get_data_dir() -> Path:
    """Directory for reviews_master.csv and reviews_metadata.json."""
    override = os.getenv("REVIEWS_DATA_DIR")
    if override:
        return Path(override)
    return _backend_root() / "data"


def get_csv_path() -> Path:
    return get_data_dir() / "reviews_master.csv"


def get_metadata_path() -> Path:
    return get_data_dir() / "reviews_metadata.json"


def get_play_store_app_id() -> str:
    """Google Play package id (default: INDmoney app per Play Store listing)."""
    return os.getenv("PLAY_STORE_APP_ID", "in.indwealth").strip()


def get_play_lang() -> str:
    """Play Store language code (lowercase; scraper-friendly)."""
    return os.getenv("PLAY_STORE_LANG", "en").strip().lower()


def get_play_country() -> str:
    """Play Store country (lowercase ISO; `IN` and `in` both accepted)."""
    return os.getenv("PLAY_STORE_COUNTRY", "in").strip().lower()


def get_fetch_max_reviews() -> int:
    raw = os.getenv("PLAY_FETCH_MAX_REVIEWS", "500")
    try:
        n = int(raw)
        return max(1, min(n, 5000))
    except ValueError:
        return 500


def get_min_review_length() -> int:
    raw = os.getenv("REVIEW_MIN_CONTENT_LENGTH", "10")
    try:
        return max(1, int(raw))
    except ValueError:
        return 10


def get_min_meaningful_words() -> int:
    raw = os.getenv("REVIEW_MIN_MEANINGFUL_WORDS", "3")
    try:
        return max(1, min(20, int(raw)))
    except ValueError:
        return 3


def get_min_meaningful_for_pulse() -> int:
    raw = os.getenv("MIN_MEANINGFUL_NEW_REVIEWS_FOR_PULSE", "5")
    try:
        return max(1, min(500, int(raw)))
    except ValueError:
        return 5


def scheduler_enabled() -> bool:
    default = "false" if os.getenv("APP_ENV", "").lower() == "production" else "true"
    return os.getenv("SCHEDULER_ENABLED", default).lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def fetch_interval_hours() -> int:
    raw = os.getenv("FETCH_INTERVAL_HOURS", "48")
    try:
        h = int(raw)
        return max(1, min(h, 24 * 14))
    except ValueError:
        return 48


def get_fetch_trigger_token() -> str:
    """Shared secret for external cron/manual protected fetch trigger."""
    return os.getenv("CRON_TRIGGER_TOKEN", "").strip()
