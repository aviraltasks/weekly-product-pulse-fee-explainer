"""POST /api/preview/create — mocked pipeline + counter."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.pulse.schemas import AnalysisJson, PulseFinalJson, PulseGenerateMeta, PulseGenerateResponse, QuoteItem, ThemeItem


def _analysis() -> AnalysisJson:
    return AnalysisJson(
        themes=[ThemeItem(name="T1"), ThemeItem(name="T2"), ThemeItem(name="T3")],
        top_3_theme_names=["T1", "T2", "T3"],
        quotes=[
            QuoteItem(theme="T1", quote="q one long enough for validation rules."),
            QuoteItem(theme="T2", quote="q two long enough for validation rules."),
            QuoteItem(theme="T3", quote="q three long enough for validation rules."),
        ],
    )


def test_preview_create_200_increments_n(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("REVIEWS_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("GROQ_API_KEY", "x")
    monkeypatch.setenv("GEMINI_API_KEY", "y")
    monkeypatch.setenv("FEE_SOURCE_URL_1", "")
    monkeypatch.setenv("FEE_SOURCE_URL_2", "")
    monkeypatch.setenv("WEEKLY_PULSE_COUNTER_PATH", str(tmp_path / "n.json"))

    pulse = PulseGenerateResponse(
        analysis=_analysis(),
        weekly_note="Note " * 10,
        actions=["a1", "a2", "a3"],
        meta=PulseGenerateMeta(
            reviews_sampled=1,
            groq_model="g",
            gemini_model="m",
            generated_at_iso="2025-01-01T00:00:00+00:00",
            note_word_count=20,
        ),
        fee=None,
    )

    from app.main import app

    with patch("app.preview.service.generate_pulse", new_callable=AsyncMock, return_value=pulse):
        with TestClient(app) as client:
            r1 = client.post("/api/preview/create")
            r2 = client.post("/api/preview/create")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["weekly_pulse_n"] == 1
    assert r2.json()["weekly_pulse_n"] == 2
    b1 = r1.json()
    assert b1["email_template_version"] == "2"
    assert b1["email"]["format_version"] == "2"
    assert "Weekly Pulse + Fee Explainer" in b1["email"]["subject"]
    assert b1["doc_append"]["weekly_pulse"] == pulse.weekly_note
    assert "doc_block_plain" in b1
    assert b1["as_on"]["display"].endswith("IST")


def test_preview_create_503_without_llm_keys(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("REVIEWS_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("WEEKLY_PULSE_COUNTER_PATH", str(tmp_path / "n.json"))
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
        r = client.post("/api/preview/create")
    assert r.status_code == 503
