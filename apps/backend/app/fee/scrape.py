"""Lightweight HTML fetch + tag strip for fee source pages."""

from __future__ import annotations

import re

import httpx

_USER_AGENT = (
    "Mozilla/5.0 (compatible; WeeklyPulseBot/1.0; +https://example.invalid) "
    "Python-httpx"
)


def strip_html_to_text(html: str, max_chars: int = 4000) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


async def fetch_page_text(url: str, *, timeout_sec: float = 25.0) -> str:
    async with httpx.AsyncClient(
        timeout=timeout_sec,
        follow_redirects=True,
        headers={"User-Agent": _USER_AGENT},
    ) as client:
        r = await client.get(url)
        r.raise_for_status()
        return strip_html_to_text(r.text)


async def fetch_page_html(
    url: str,
    *,
    timeout_sec: float = 30.0,
    max_bytes: int = 2_000_000,
) -> str:
    """Raw HTML for structured extraction (e.g. INDmoney FAQ)."""
    async with httpx.AsyncClient(
        timeout=timeout_sec,
        follow_redirects=True,
        headers={"User-Agent": _USER_AGENT},
    ) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.text[:max_bytes]


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_indmoney_exit_load_faq(html: str) -> str | None:
    """
    Extract answer under FAQ: 'What is the exit load of the fund?' (INDmoney SBI Large Cap page).
    Looks for the paragraph containing 0.25% / 0.1% tiers and the fee definition.
    """
    plain = strip_html_to_text(html, max_chars=600_000)

    # Full expected paragraph (tiers + definition)
    m = re.search(
        r"(The exit load is 0\.25%[\s\S]{0,900}?stipulated period[\s\S]{0,80}?1\s*year\.)",
        plain,
        re.IGNORECASE,
    )
    if m:
        return _normalize_ws(m.group(1))

    m = re.search(
        r"(The exit load is 0\.25%[^.]*?0-30[^.]*?0\.1%[^.]*?90[^.]*?Days[^.]*?\.\s*Exit load is a fee[^.]*?\.)",
        plain,
        re.IGNORECASE,
    )
    if m:
        return _normalize_ws(m.group(1))

    # Shorter: at least both rates + one sentence
    m = re.search(
        r"(The exit load is 0\.25%[^.]{10,500}?0\.1%[^.]{5,200}?\.)",
        plain,
        re.IGNORECASE,
    )
    if m:
        return _normalize_ws(m.group(1))

    # After FAQ question heading (loose)
    m = re.search(
        r"What is the exit load of the fund\??\s*(.{30,1200}?)(?=\s*(?:What |How |Why |Which |When |Does |Is |Are |Can |Will |Should |\Z))",
        plain,
        re.IGNORECASE | re.DOTALL,
    )
    if m and "0.25" in m.group(1):
        return _normalize_ws(m.group(1))

    return None
