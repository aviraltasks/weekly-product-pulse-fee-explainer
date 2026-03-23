"""Runtime storage mode guards for hosts with ephemeral local disk."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def storage_mode() -> str:
    """
    'persistent' (expected durable disk) or 'ephemeral' (free-tier best effort).
    """
    mode = os.getenv("STORAGE_MODE", "ephemeral").strip().lower()
    if mode not in {"persistent", "ephemeral"}:
        return "ephemeral"
    return mode


def warn_if_ephemeral(context: str) -> None:
    if storage_mode() == "ephemeral":
        logger.warning(
            "Ephemeral storage mode: '%s' may reset on restart/redeploy.",
            context,
        )
