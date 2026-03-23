"""Pulse / LLM configuration (lazy env reads)."""

from __future__ import annotations

import os


def get_groq_api_key() -> str:
    return os.getenv("GROQ_API_KEY", "").strip()


def get_groq_model() -> str:
    return os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()


def get_gemini_api_key() -> str:
    return os.getenv("GEMINI_API_KEY", "").strip()


def get_gemini_model() -> str:
    # Default: documented id for generateContent — override with GEMINI_MODEL in .env
    return os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview").strip()


def get_pulse_sample_max() -> int:
    # Default stays under typical Groq on-demand ~12k-token-per-request limits (prompt + system).
    raw = os.getenv("PULSE_SAMPLE_MAX_REVIEWS", "55")
    try:
        n = int(raw)
        return max(10, min(n, 300))
    except ValueError:
        return 55


def get_pulse_truncate_chars() -> int:
    raw = os.getenv("PULSE_TRUNCATE_CHARS", "280")
    try:
        n = int(raw)
        return max(100, min(n, 800))
    except ValueError:
        return 280


def get_llm_max_retries() -> int:
    raw = os.getenv("LLM_MAX_RETRIES", "3")
    try:
        return max(1, min(int(raw), 8))
    except ValueError:
        return 3


def get_llm_retry_backoff_sec() -> float:
    raw = os.getenv("LLM_RETRY_BACKOFF_SEC", "1.2")
    try:
        return max(0.2, float(raw))
    except ValueError:
        return 1.2


def llm_keys_configured() -> bool:
    return bool(get_groq_api_key() and get_gemini_api_key())
