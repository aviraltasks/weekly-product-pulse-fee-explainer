"""Fee explainer configuration (env + paths)."""

from __future__ import annotations

import os
from pathlib import Path


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_fee_defaults_path() -> Path:
    return _backend_root() / "data" / "fee_defaults.json"


def get_fee_source2_hardcoded_path() -> Path:
    return _backend_root() / "data" / "fee_source2_hardcoded.json"


# Default public URLs (override with FEE_SOURCE_URL_1 / _2; set env to empty string to disable fee block)
DEFAULT_FEE_SOURCE_URL_1 = (
    "https://www.indmoney.com/mutual-funds/sbi-large-cap-fund-direct-growth-3046"
)
DEFAULT_FEE_SOURCE_URL_2 = "https://investor.sebi.gov.in/exit_load.html"


def get_fee_cache_path() -> Path:
    override = os.getenv("FEE_CACHE_PATH")
    if override:
        return Path(override)
    return _backend_root() / "data" / "fee_explainer_cache.json"


def get_fee_scenario_override() -> str | None:
    v = os.getenv("FEE_SCENARIO_TITLE", "").strip()
    return v or None


def get_source_url_1() -> str:
    v = os.getenv("FEE_SOURCE_URL_1")
    if v is not None:
        return v.strip()
    return DEFAULT_FEE_SOURCE_URL_1


def get_source_url_2() -> str:
    v = os.getenv("FEE_SOURCE_URL_2")
    if v is not None:
        return v.strip()
    return DEFAULT_FEE_SOURCE_URL_2


def fee_urls_configured() -> bool:
    return bool(get_source_url_1() and get_source_url_2())
