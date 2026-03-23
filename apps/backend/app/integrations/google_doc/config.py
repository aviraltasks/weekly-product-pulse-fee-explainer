"""Google Docs API — env-based configuration."""

from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Any


def get_google_doc_id() -> str:
    return os.getenv("GOOGLE_DOC_ID", "").strip()


def get_service_account_file() -> str:
    """Path to service account JSON (not committed; share target Doc with this SA email)."""
    return os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "").strip()


def get_service_account_json() -> str:
    """
    Raw service account JSON string.
    Recommended for hosted environments where file mounts are awkward.
    """
    return os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()


def google_doc_append_configured() -> bool:
    return bool(
        get_google_doc_id() and (get_service_account_json() or get_service_account_file())
    )


def assert_service_account_path() -> Path:
    p = Path(get_service_account_file())
    if not p.is_file():
        raise FileNotFoundError(
            f"GOOGLE_SERVICE_ACCOUNT_FILE not found: {p}",
        )
    return p


def load_service_account_info() -> dict[str, Any]:
    """
    Return service-account credential payload from env JSON or file path.
    Priority: GOOGLE_SERVICE_ACCOUNT_JSON > GOOGLE_SERVICE_ACCOUNT_FILE.
    """
    raw = get_service_account_json()
    if raw:
        try:
            obj = json.loads(raw)
            if not isinstance(obj, dict):
                raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON must decode to an object")
            return obj
        except json.JSONDecodeError as e:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON") from e

    path = assert_service_account_path()
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to read service account JSON file: {path}") from e
    if not isinstance(obj, dict):
        raise ValueError("Service account file JSON must decode to an object")
    return obj
