"""Read / write fee_explainer_cache.json."""

from __future__ import annotations

import json
from pathlib import Path

from app.common.storage_mode import warn_if_ephemeral
from app.fee.schemas import FeeCachePayload


def read_cache(path: Path) -> FeeCachePayload | None:
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return FeeCachePayload.model_validate(raw)
    except (json.JSONDecodeError, OSError, ValueError):
        return None


def write_cache(path: Path, payload: FeeCachePayload) -> None:
    warn_if_ephemeral("fee_explainer_cache.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
