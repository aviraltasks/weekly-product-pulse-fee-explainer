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
