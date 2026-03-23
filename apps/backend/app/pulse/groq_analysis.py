"""LLM1: Groq OpenAI-compatible chat completions → AnalysisJson."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from app.pulse import config as pulse_config
from app.pulse.errors import PulsePipelineError
from app.pulse.json_utils import extract_json_object
from app.pulse.prompts import GROQ_SYSTEM, build_groq_user_payload
from app.pulse.schemas import AnalysisJson

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def _groq_chat_sync(
    *,
    user_content: str,
    model: str,
    api_key: str,
) -> str:
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": GROQ_SYSTEM},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    with httpx.Client(timeout=120.0) as client:
        r = client.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
    if r.status_code >= 400:
        raise PulsePipelineError(f"Groq HTTP {r.status_code}: {r.text[:500]}")
    data = r.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise PulsePipelineError(f"Unexpected Groq response shape: {data!r}") from e


async def run_groq_analysis(samples: list[dict[str, str]]) -> AnalysisJson:
    """Two-step pipeline call site #1 — Groq only."""
    api_key = pulse_config.get_groq_api_key()
    if not api_key:
        raise PulsePipelineError("GROQ_API_KEY is not set.")
    model = pulse_config.get_groq_model()
    user_content = build_groq_user_payload(samples)

    async def _once() -> AnalysisJson:
        raw = await asyncio.to_thread(
            _groq_chat_sync,
            user_content=user_content,
            model=model,
            api_key=api_key,
        )
        try:
            obj = extract_json_object(raw)
            return AnalysisJson.model_validate(obj)
        except Exception as e:
            logger.exception("Groq JSON parse/validate failed")
            raise PulsePipelineError(f"Groq output invalid: {e}") from e

    from app.pulse.retry_util import retry_async

    return await retry_async(
        _once,
        retries=pulse_config.get_llm_max_retries(),
        backoff_sec=pulse_config.get_llm_retry_backoff_sec(),
        label="groq",
    )
