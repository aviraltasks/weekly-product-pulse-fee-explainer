"""Fee explainer: cache, refresh (scrape INDmoney FAQ), merge-ready block."""

from __future__ import annotations

from datetime import datetime, timezone

from app.fee.cache_io import read_cache, write_cache
from app.fee.config import (
    fee_urls_configured,
    get_fee_cache_path,
    get_fee_scenario_override,
    get_source_url_1,
    get_source_url_2,
)
from app.fee.defaults_loader import build_explanation_bullets, load_fee_scenario
from app.fee.schemas import FeeCachePayload, FeeExplainerBlock
from app.fee.scrape import (
    extract_indmoney_exit_load_faq,
    fetch_page_html,
    strip_html_to_text,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_block_from_defaults(
    *,
    last_checked_iso: str,
    source_links: tuple[str, str],
) -> FeeExplainerBlock:
    title = load_fee_scenario()
    override = get_fee_scenario_override()
    if override:
        title = override
    bullets = build_explanation_bullets(None)
    return FeeExplainerBlock(
        fee_scenario=title,
        explanation_bullets=bullets,
        source_links=[source_links[0], source_links[1]],
        last_checked_iso=last_checked_iso,
    )


def get_fee_explainer_or_none() -> FeeExplainerBlock | None:
    """Return cached or fresh-from-defaults fee block; None if URLs explicitly disabled."""
    if not fee_urls_configured():
        return None
    u1, u2 = get_source_url_1(), get_source_url_2()
    cache_path = get_fee_cache_path()
    cached = read_cache(cache_path)
    if cached and len(cached.source_links) >= 2:
        return FeeExplainerBlock(
            fee_scenario=cached.fee_scenario,
            explanation_bullets=cached.explanation_bullets,
            source_links=[cached.source_links[0], cached.source_links[1]],
            last_checked_iso=cached.last_checked_iso,
        )
    block = build_block_from_defaults(
        last_checked_iso=_utc_now_iso(),
        source_links=(u1, u2),
    )
    write_cache(
        cache_path,
        FeeCachePayload(
            fee_scenario=block.fee_scenario,
            explanation_bullets=block.explanation_bullets,
            source_links=[u1, u2],
            last_checked_iso=block.last_checked_iso,
            excerpts={},
        ),
    )
    return block


async def refresh_fee_explainer() -> FeeExplainerBlock:
    """
    Re-fetch Source 1 (INDmoney HTML) and extract FAQ answer; Source 2 text is hardcoded (no scrape).
    """
    if not fee_urls_configured():
        raise ValueError("FEE_SOURCE_URL_1 and FEE_SOURCE_URL_2 must be set for refresh")
    u1, u2 = get_source_url_1(), get_source_url_2()
    excerpts: dict[str, str] = {}
    indmoney_paragraph: str | None = None

    try:
        html = await fetch_page_html(u1)
        indmoney_paragraph = extract_indmoney_exit_load_faq(html)
        if indmoney_paragraph:
            excerpts[u1] = indmoney_paragraph[:4000]
        else:
            excerpts[u1] = strip_html_to_text(html, max_chars=2500)
    except Exception as exc:  # noqa: BLE001
        excerpts[u1] = f"(fetch failed: {exc})"

    excerpts[u2] = (
        "Hardcoded from fee_source2_hardcoded.json — SEBI investor exit-load article "
        "(“How does exit load work?”) summarized; page not scraped."
    )

    title = load_fee_scenario()
    override = get_fee_scenario_override()
    if override:
        title = override
    bullets = build_explanation_bullets(indmoney_paragraph)
    now = _utc_now_iso()
    payload = FeeCachePayload(
        fee_scenario=title,
        explanation_bullets=bullets,
        source_links=[u1, u2],
        last_checked_iso=now,
        excerpts=excerpts,
    )
    write_cache(get_fee_cache_path(), payload)
    return FeeExplainerBlock(
        fee_scenario=title,
        explanation_bullets=bullets,
        source_links=[u1, u2],
        last_checked_iso=now,
    )
