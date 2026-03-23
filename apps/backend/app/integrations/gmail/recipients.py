"""Filter send list against subscriber store (admin-selected addresses)."""

from __future__ import annotations


def resolve_recipients(
    requested: list[str],
    *,
    allowed_lower_to_canonical: dict[str, str],
    strict: bool,
) -> tuple[list[str], list[str]]:
    """
    Returns (send_to, rejected).
    If not strict, all non-empty trimmed emails are allowed (dev/demo).
    If strict, only keys in allowed_lower_to_canonical.
    """
    seen: set[str] = set()
    send_to: list[str] = []
    rejected: list[str] = []

    for raw in requested:
        e = (raw or "").strip()
        if not e:
            continue
        key = e.lower()
        if key in seen:
            continue
        seen.add(key)
        if not strict:
            send_to.append(e)
            continue
        if key in allowed_lower_to_canonical:
            send_to.append(allowed_lower_to_canonical[key])
        else:
            rejected.append(e)

    return send_to, rejected
