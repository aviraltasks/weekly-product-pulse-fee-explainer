"""Recipient filtering (strict vs open)."""

from __future__ import annotations

from app.integrations.gmail.recipients import resolve_recipients


def test_strict_allows_only_subscribers() -> None:
    allowed = {"a@x.com": "a@x.com", "b@x.com": "B@x.com"}
    send_to, rejected = resolve_recipients(
        ["a@x.com", "unknown@y.com"],
        allowed_lower_to_canonical=allowed,
        strict=True,
    )
    assert send_to == ["a@x.com"]
    assert rejected == ["unknown@y.com"]


def test_non_strict_allows_all() -> None:
    send_to, rejected = resolve_recipients(
        ["any@where.com"],
        allowed_lower_to_canonical={},
        strict=False,
    )
    assert send_to == ["any@where.com"]
    assert rejected == []
