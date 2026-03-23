"""GET/POST /api/subscribers."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_subscribe_and_list(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("SUBSCRIBERS_STORE_PATH", str(tmp_path / "sub.json"))
    from app.main import app

    with TestClient(app) as client:
        r = client.post("/api/subscribers", json={"email": "user@example.com"})
        assert r.status_code == 200
        assert r.json()["email"] == "user@example.com"
        r2 = client.get("/api/subscribers")
    assert r2.status_code == 200
    assert r2.json()["count"] == 1


def test_subscribe_invalid_email(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("SUBSCRIBERS_STORE_PATH", str(tmp_path / "sub.json"))
    from app.main import app

    with TestClient(app) as client:
        r = client.post("/api/subscribers", json={"email": "not-an-email"})
    assert r.status_code == 422
