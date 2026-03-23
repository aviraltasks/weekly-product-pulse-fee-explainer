"""Pulse pipeline: sampling, ordering of LLM calls (mocked), schema."""

from __future__ import annotations

import pytest

from app.pulse.errors import PulsePipelineError
from app.pulse.pipeline import generate_pulse
from app.pulse.schemas import (
    AnalysisJson,
    PulseFinalJson,
    QuoteItem,
    ThemeItem,
    clamp_note_to_max_words,
    count_words,
)
from app.reviews import config as reviews_config
from app.reviews import csv_store


@pytest.fixture
def reviews_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("REVIEWS_DATA_DIR", str(tmp_path))
    return tmp_path


def _two_rows():
    return [
        {
            "review_id": "a1",
            "user_name": "u",
            "content": "This is a longer review about the app performance and stability concerns.",
            "score": "5",
            "review_created_version": "",
            "at_iso": "2025-02-01T00:00:00+00:00",
            "thumbs_up": "0",
            "reply_content": "",
            "replied_at_iso": "",
            "app_version": "",
            "fetched_at_iso": "2025-02-02T00:00:00+00:00",
        },
        {
            "review_id": "b2",
            "user_name": "v",
            "content": "Another review about KYC onboarding and verification process here.",
            "score": "4",
            "review_created_version": "",
            "at_iso": "2025-02-03T00:00:00+00:00",
            "thumbs_up": "1",
            "reply_content": "",
            "replied_at_iso": "",
            "app_version": "",
            "fetched_at_iso": "2025-02-02T00:00:00+00:00",
        },
    ]


def test_clamp_note_words() -> None:
    long_note = "word " * 300
    out, t = clamp_note_to_max_words(long_note, max_words=250)
    assert t is True
    assert count_words(out) <= 251


@pytest.mark.asyncio
async def test_generate_empty_csv_raises(reviews_dir, monkeypatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "x")
    monkeypatch.setenv("GEMINI_API_KEY", "y")
    with pytest.raises(PulsePipelineError, match="No reviews"):
        await generate_pulse()


@pytest.mark.asyncio
async def test_generate_calls_groq_then_gemini(reviews_dir, monkeypatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "x")
    monkeypatch.setenv("GEMINI_API_KEY", "y")
    csv_store.merge_new_reviews(reviews_config.get_csv_path(), _two_rows())

    analysis = AnalysisJson(
        themes=[
            ThemeItem(name="App performance"),
            ThemeItem(name="KYC"),
            ThemeItem(name="Support"),
        ],
        top_3_theme_names=["App performance", "KYC", "Support"],
        quotes=[
            QuoteItem(theme="App performance", quote="quote one about performance here."),
            QuoteItem(theme="KYC", quote="quote two about kyc onboarding process here."),
            QuoteItem(theme="Support", quote="quote three about customer support experience."),
        ],
    )
    final = PulseFinalJson(
        weekly_note=("brief note " * 20).strip(),
        actions=["Action one line", "Action two line", "Action three line"],
    )

    order: list[str] = []

    async def fake_groq(samples):
        order.append("groq")
        assert samples and all("content" in s for s in samples)
        return analysis

    async def fake_gem(a):
        order.append("gemini")
        assert a is analysis
        return final

    from unittest.mock import patch

    with (
        patch("app.pulse.pipeline.run_groq_analysis", side_effect=fake_groq),
        patch("app.pulse.pipeline.run_gemini_final", side_effect=fake_gem),
    ):
        out = await generate_pulse()

    assert order == ["groq", "gemini"]
    assert out.analysis == analysis
    assert out.actions == final.actions
    assert out.meta.reviews_sampled >= 2
