"""Subscribers JSON store path."""

from __future__ import annotations

import os
from pathlib import Path


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_subscribers_store_path() -> Path:
    override = os.getenv("SUBSCRIBERS_STORE_PATH")
    if override:
        return Path(override)
    return _backend_root() / "data" / "subscribers.json"
