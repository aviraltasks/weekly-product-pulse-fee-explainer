"""POST /api/pulse/generate — status codes with mocks / empty data."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


def test_pulse_generate_503_without_keys(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("REVIEWS_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    from app.reviews import csv_store
    from app.reviews import config as reviews_config

    csv_store.merge_new_reviews(
        reviews_config.get_csv_path(),
        [
            {
                "review_id": "r1",
                "user_name": "u",
                "content": "Enough text here for sampling pipeline to run in principle.",
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
    from app.main import app

    with TestClient(app) as client:
        r = client.post("/api/pulse/generate")
    assert r.status_code == 503


def test_pulse_generate_400_empty_csv(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("REVIEWS_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("GROQ_API_KEY", "x")
    monkeypatch.setenv("GEMINI_API_KEY", "y")
    from app.main import app

    with TestClient(app) as client:
        r = client.post("/api/pulse/generate")
    assert r.status_code == 400


def test_pulse_generate_200_mocked_llms(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("REVIEWS_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("GROQ_API_KEY", "x")
    monkeypatch.setenv("GEMINI_API_KEY", "y")
    monkeypatch.setenv("FEE_SOURCE_URL_1", "")
    monkeypatch.setenv("FEE_SOURCE_URL_2", "")
    from app.reviews import csv_store
    from app.reviews import config as reviews_config

    csv_store.merge_new_reviews(
        reviews_config.get_csv_path(),
        [
            {
                "review_id": "r1",
                "user_name": "u",
                "content": "Enough text here for sampling pipeline to run in principle.",
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
    from app.pulse.schemas import AnalysisJson, PulseFinalJson, QuoteItem, ThemeItem
    from app.main import app

    analysis = AnalysisJson(
        themes=[ThemeItem(name="T1"), ThemeItem(name="T2"), ThemeItem(name="T3")],
        top_3_theme_names=["T1", "T2", "T3"],
        quotes=[
            QuoteItem(theme="T1", quote="q one long enough for validation rules."),
            QuoteItem(theme="T2", quote="q two long enough for validation rules."),
            QuoteItem(theme="T3", quote="q three long enough for validation rules."),
        ],
    )
    final = PulseFinalJson(
        weekly_note="Summary paragraph for leadership. " * 5,
        actions=["a1", "a2", "a3"],
    )

    with (
        patch("app.pulse.pipeline.run_groq_analysis", new_callable=AsyncMock, return_value=analysis),
        patch("app.pulse.pipeline.run_gemini_final", new_callable=AsyncMock, return_value=final),
    ):
        with TestClient(app) as client:
            r = client.post("/api/pulse/generate")
    assert r.status_code == 200
    body = r.json()
    assert body["weekly_note"]
    assert len(body["actions"]) == 3
    assert "analysis" in body
    assert body.get("fee") is None


def test_pulse_generate_200_includes_fee_when_configured(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("REVIEWS_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("GROQ_API_KEY", "x")
    monkeypatch.setenv("GEMINI_API_KEY", "y")
    monkeypatch.setenv("FEE_SOURCE_URL_1", "https://official-one.example")
    monkeypatch.setenv("FEE_SOURCE_URL_2", "https://official-two.example")
    monkeypatch.setenv("FEE_CACHE_PATH", str(tmp_path / "fee_cache.json"))
    from app.reviews import csv_store
    from app.reviews import config as reviews_config

    csv_store.merge_new_reviews(
        reviews_config.get_csv_path(),
        [
            {
                "review_id": "r1",
                "user_name": "u",
                "content": "Enough text here for sampling pipeline to run in principle.",
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
    from app.pulse.schemas import AnalysisJson, PulseFinalJson, QuoteItem, ThemeItem
    from app.main import app

    analysis = AnalysisJson(
        themes=[ThemeItem(name="T1"), ThemeItem(name="T2"), ThemeItem(name="T3")],
        top_3_theme_names=["T1", "T2", "T3"],
        quotes=[
            QuoteItem(theme="T1", quote="q one long enough for validation rules."),
            QuoteItem(theme="T2", quote="q two long enough for validation rules."),
            QuoteItem(theme="T3", quote="q three long enough for validation rules."),
        ],
    )
    final = PulseFinalJson(
        weekly_note="Summary paragraph for leadership. " * 5,
        actions=["a1", "a2", "a3"],
    )

    with (
        patch("app.pulse.pipeline.run_groq_analysis", new_callable=AsyncMock, return_value=analysis),
        patch("app.pulse.pipeline.run_gemini_final", new_callable=AsyncMock, return_value=final),
    ):
        with TestClient(app) as client:
            r = client.post("/api/pulse/generate")
    assert r.status_code == 200
    fee = r.json()["fee"]
    assert fee is not None
    assert len(fee["explanation_bullets"]) <= 6
    assert len(fee["source_links"]) == 2
