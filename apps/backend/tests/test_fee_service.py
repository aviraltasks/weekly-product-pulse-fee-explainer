"""Fee cache + refresh (mocked HTTP)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.fee.cache_io import read_cache
from app.fee.service import get_fee_explainer_or_none, refresh_fee_explainer


@pytest.mark.asyncio
async def test_refresh_writes_cache_and_two_excerpts(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("FEE_SOURCE_URL_1", "https://source-one.example/doc")
    monkeypatch.setenv("FEE_SOURCE_URL_2", "https://source-two.example/doc")
    cache = tmp_path / "fee_explainer_cache.json"
    monkeypatch.setenv("FEE_CACHE_PATH", str(cache))

    sample_html = """
    <p>What is the exit load of the fund?</p>
    <p>The exit load is 0.25% if redeemed in 0-30 Days, 0.1% if redeemed in 30-90 Days.
    Exit load is a fee levied for exiting the fund earlier than a stipulated period, usually 1 year.</p>
    """

    with patch(
        "app.fee.service.fetch_page_html",
        new_callable=AsyncMock,
        return_value=sample_html,
    ):
        block = await refresh_fee_explainer()

    assert block.fee_scenario
    assert len(block.explanation_bullets) <= 6
    assert len(block.source_links) == 2
    assert block.source_links[0] == "https://source-one.example/doc"
    assert "0.25%" in block.explanation_bullets[0]

    cached = read_cache(cache)
    assert cached is not None
    assert len(cached.excerpts) == 2
    assert "0.25%" in cached.excerpts["https://source-one.example/doc"]
    assert "Hardcoded" in cached.excerpts["https://source-two.example/doc"]


def test_get_fee_returns_cached_block(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("FEE_SOURCE_URL_1", "https://a.example")
    monkeypatch.setenv("FEE_SOURCE_URL_2", "https://b.example")
    monkeypatch.setenv("FEE_CACHE_PATH", str(tmp_path / "c.json"))

    b1 = get_fee_explainer_or_none()
    assert b1 is not None
    b2 = get_fee_explainer_or_none()
    assert b2 is not None
    assert b1.last_checked_iso == b2.last_checked_iso


def test_get_fee_none_without_urls(monkeypatch) -> None:
    monkeypatch.setenv("FEE_SOURCE_URL_1", "")
    monkeypatch.setenv("FEE_SOURCE_URL_2", "")
    assert get_fee_explainer_or_none() is None
