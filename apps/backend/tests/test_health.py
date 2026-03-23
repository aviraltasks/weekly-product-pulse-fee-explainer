"""Health endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_api_health_returns_ok() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data.get("email_format_version") == "2"
    assert response.headers.get("X-Email-Format-Version") == "2"
