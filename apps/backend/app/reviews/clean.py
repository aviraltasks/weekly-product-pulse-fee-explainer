"""Normalize and filter scraped reviews before CSV merge."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "]",
)
_ALLOWED_TEXT_RE = re.compile(r"^[A-Za-z0-9\u0900-\u097F\s\.,;:!?'\-_/()%&+@#\[\]\{\}\*\"`]+$")
_WORD_RE = re.compile(r"[A-Za-z\u0900-\u097F]{2,}")


def _iso(dt: Any) -> str:
    if dt is None:
        return ""
    if isinstance(dt, datetime):
        return dt.isoformat()
    return str(dt)


def is_meaningful_content(
    content: str,
    *,
    min_content_length: int,
    min_word_count: int = 3,
) -> bool:
    """
    Quality gate for analysis-ready reviews.
    Allows Latin + Devanagari text; rejects emoji-heavy / noisy content.
    """
    text = (content or "").strip()
    if len(text) < min_content_length:
        return False
    if _EMOJI_RE.search(text):
        return False
    if not _ALLOWED_TEXT_RE.match(text):
        return False
    words = _WORD_RE.findall(text)
    if len(words) < min_word_count:
        return False
    total_alpha = sum(1 for ch in text if ch.isalpha())
    if total_alpha < min_content_length // 2:
        return False
    return True


def normalize_scraped_review(
    raw: dict[str, Any],
    *,
    fetched_at_iso: str,
    min_content_length: int,
    min_word_count: int = 3,
) -> dict[str, str] | None:
    """
    Map google-play-scraper row → CSV row; drop invalid / too-short content.
    """
    rid = str(raw.get("reviewId") or "").strip()
    content = (raw.get("content") or "").strip()
    if not rid or not is_meaningful_content(
        content,
        min_content_length=min_content_length,
        min_word_count=min_word_count,
    ):
        return None
    user_name = (raw.get("userName") or "").strip()
    score = raw.get("score")
    try:
        score_s = str(int(score)) if score is not None else ""
    except (TypeError, ValueError):
        score_s = ""
    rcv = (raw.get("reviewCreatedVersion") or "").strip()
    at_iso = _iso(raw.get("at"))
    thumbs = raw.get("thumbsUpCount")
    try:
        thumbs_s = str(int(thumbs)) if thumbs is not None else ""
    except (TypeError, ValueError):
        thumbs_s = ""
    reply = (raw.get("replyContent") or "").strip().replace("\r\n", "\n")
    replied_at = _iso(raw.get("repliedAt"))
    app_ver = (raw.get("appVersion") or "").strip()

    return {
        "review_id": rid,
        "user_name": user_name,
        "content": content,
        "score": score_s,
        "review_created_version": rcv,
        "at_iso": at_iso,
        "thumbs_up": thumbs_s,
        "reply_content": reply,
        "replied_at_iso": replied_at,
        "app_version": app_ver,
        "fetched_at_iso": fetched_at_iso,
    }
