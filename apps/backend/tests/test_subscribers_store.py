"""Subscribers JSON store."""

from __future__ import annotations

from app.subscribers.store import add_subscriber, list_subscribers, subscriber_email_set


def test_add_and_list_dedupes(tmp_path) -> None:
    p = tmp_path / "s.json"
    add_subscriber("A@Example.com", path=p)
    add_subscriber("a@example.com", path=p)
    rows = list_subscribers(path=p)
    assert len(rows) == 1
    assert subscriber_email_set(path=p) == {"a@example.com"}


def test_add_second_email(tmp_path) -> None:
    p = tmp_path / "s.json"
    add_subscriber("one@test.com", path=p)
    add_subscriber("two@test.com", path=p)
    assert len(list_subscribers(path=p)) == 2
