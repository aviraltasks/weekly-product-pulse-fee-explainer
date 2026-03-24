"""POST /api/integrations/gmail/send."""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient


def test_gmail_send_503_when_not_configured(monkeypatch) -> None:
    monkeypatch.delenv("GMAIL_SMTP_USER", raising=False)
    monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)
    from app.main import app

    with TestClient(app) as client:
        r = client.post(
            "/api/integrations/gmail/send",
            json={
                "to_emails": ["a@b.com"],
                "subject": "S",
                "body_plain": "Body",
            },
        )
    assert r.status_code == 503


def test_gmail_send_200_mocked(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GMAIL_SMTP_USER", "me@gmail.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "abcdefghijklmnop")
    monkeypatch.setenv("SUBSCRIBERS_STORE_PATH", str(tmp_path / "sub.json"))
    monkeypatch.setenv("GMAIL_STRICT_RECIPIENTS", "true")

    from app.subscribers.store import add_subscriber

    add_subscriber("friend@example.com", path=tmp_path / "sub.json")

    from app.main import app

    with patch("app.integrations.gmail.router.send_email") as mock_send:
        with TestClient(app) as client:
            r = client.post(
                "/api/integrations/gmail/send",
                json={
                    "to_emails": ["friend@example.com"],
                    "subject": "Weekly Pulse test",
                    "body_plain": "Hello",
                    "body_html": "<p>Hello</p>",
                },
            )
    assert r.status_code == 200
    data = r.json()
    assert data["sent_to"] == ["friend@example.com"]
    mock_send.assert_called_once()
    assert mock_send.call_args.kwargs.get("attachments") is None


def test_gmail_send_with_quotes_attachment_mocked(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GMAIL_SMTP_USER", "me@gmail.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "abcdefghijklmnop")
    monkeypatch.setenv("SUBSCRIBERS_STORE_PATH", str(tmp_path / "sub.json"))
    monkeypatch.setenv("GMAIL_STRICT_RECIPIENTS", "true")
    monkeypatch.setenv("REVIEWS_DATA_DIR", str(tmp_path / "rev"))

    from app.subscribers.store import add_subscriber
    from app.reviews import config, csv_store

    (tmp_path / "rev").mkdir(parents=True, exist_ok=True)
    csv_store.merge_new_reviews(
        config.get_csv_path(),
        [
            {
                "review_id": "a1",
                "user_name": "X",
                "content": "Attached quote line long enough",
                "score": "5",
                "review_created_version": "",
                "at_iso": "2025-01-01T00:00:00+00:00",
                "thumbs_up": "0",
                "reply_content": "",
                "replied_at_iso": "",
                "app_version": "",
                "fetched_at_iso": "2025-01-02T00:00:00+00:00",
            }
        ],
    )
    add_subscriber("friend@example.com", path=tmp_path / "sub.json")

    from app.main import app

    with patch("app.integrations.gmail.router.send_email") as mock_send:
        with TestClient(app) as client:
            r = client.post(
                "/api/integrations/gmail/send",
                json={
                    "to_emails": ["friend@example.com"],
                    "subject": "Weekly Pulse test",
                    "body_plain": "Hello",
                    "body_html": "<p>Hello</p>",
                    "attach_quotes_export": True,
                },
            )
    assert r.status_code == 200
    att = mock_send.call_args.kwargs.get("attachments")
    assert att is not None
    assert len(att) == 1
    assert att[0][0] == "review_quotes_export.csv"
    assert b"feedback_id" in att[0][1]
    assert b"Attached quote line long enough" in att[0][1]


def test_gmail_send_400_when_strict_and_unknown(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GMAIL_SMTP_USER", "me@gmail.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "abcdefghijklmnop")
    monkeypatch.setenv("SUBSCRIBERS_STORE_PATH", str(tmp_path / "sub.json"))
    monkeypatch.setenv("GMAIL_STRICT_RECIPIENTS", "true")
    from app.main import app

    with TestClient(app) as client:
        r = client.post(
            "/api/integrations/gmail/send",
            json={
                "to_emails": ["stranger@example.com"],
                "subject": "S",
                "body_plain": "B",
            },
        )
    assert r.status_code == 400
