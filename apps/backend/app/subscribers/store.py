"""Persist subscribers in JSON (dedupe by email, case-insensitive)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from app.common.storage_mode import warn_if_ephemeral

from app.subscribers.config import get_subscribers_store_path


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_raw(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"subscribers": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"subscribers": []}


def _write(path: Path, data: dict[str, Any]) -> None:
    warn_if_ephemeral("subscribers.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def list_subscribers(path: Path | None = None) -> list[dict[str, str]]:
    p = path or get_subscribers_store_path()
    raw = _read_raw(p)
    subs = raw.get("subscribers") or []
    if not isinstance(subs, list):
        return []
    out: list[dict[str, str]] = []
    for row in subs:
        if isinstance(row, dict) and row.get("email"):
            out.append(
                {
                    "email": str(row["email"]).strip(),
                    "subscribed_at_iso": str(row.get("subscribed_at_iso") or ""),
                }
            )
    return out


def subscriber_email_set(path: Path | None = None) -> set[str]:
    return {s["email"].lower() for s in list_subscribers(path)}


def add_subscriber(email: str, *, path: Path | None = None) -> dict[str, str]:
    """Add or refresh timestamp if email already exists (idempotent subscribe)."""
    p = path or get_subscribers_store_path()
    raw = _read_raw(p)
    subs = raw.get("subscribers") or []
    if not isinstance(subs, list):
        subs = []
    key = email.strip().lower()
    now = _utc_iso()
    found = False
    for row in subs:
        if isinstance(row, dict) and str(row.get("email", "")).strip().lower() == key:
            row["email"] = email.strip()
            row["subscribed_at_iso"] = now
            found = True
            break
    if not found:
        subs.append({"email": email.strip(), "subscribed_at_iso": now})
    raw["subscribers"] = subs
    _write(p, raw)
    return {"email": email.strip(), "subscribed_at_iso": now}
