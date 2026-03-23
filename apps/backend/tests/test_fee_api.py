"""GET /api/fee and POST /api/fee/refresh."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


def test_fee_get_503_when_not_configured(monkeypatch) -> None:
    monkeypatch.setenv("FEE_SOURCE_URL_1", "")
    monkeypatch.setenv("FEE_SOURCE_URL_2", "")
    from app.main import app

    with TestClient(app) as client:
        r = client.get("/api/fee")
    assert r.status_code == 503


def test_fee_refresh_200_mocked(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("FEE_SOURCE_URL_1", "https://one.example")
    monkeypatch.setenv("FEE_SOURCE_URL_2", "https://two.example")
    monkeypatch.setenv("FEE_CACHE_PATH", str(tmp_path / "fee.json"))

    sample_html = """
    <html><body>
    <p>What is the exit load of the fund?</p>
    <p>The exit load is 0.25% if redeemed in 0-30 Days, 0.1% if redeemed in 30-90 Days.
    Exit load is a fee levied for exiting the fund earlier than a stipulated period, usually 1 year.</p>
    </body></html>
    """

    with patch(
        "app.fee.service.fetch_page_html",
        new_callable=AsyncMock,
        return_value=sample_html,
    ):
        from app.main import app

        with TestClient(app) as client:
            r = client.post("/api/fee/refresh")
    assert r.status_code == 200
    data = r.json()
    assert len(data["source_links"]) == 2
    assert len(data["explanation_bullets"]) <= 6
    assert "0.25%" in data["explanation_bullets"][0]
