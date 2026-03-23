"""LLM2: Gemini — weekly note + actions; input = analysis JSON only."""

from __future__ import annotations

import asyncio
import logging

from app.pulse import config as pulse_config
from app.pulse.errors import PulsePipelineError
from app.pulse.json_utils import extract_json_object
from app.pulse.prompts import build_gemini_user_prompt
from app.pulse.schemas import AnalysisJson, PulseFinalJson

logger = logging.getLogger(__name__)


def _gemini_generate_sync(prompt: str, model: str, api_key: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    m = genai.GenerativeModel(model)
    r = m.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(temperature=0.35),
    )
    text = getattr(r, "text", None) or ""
    if not text.strip():
        raise PulsePipelineError("Gemini returned empty text (blocked or no candidates).")
    return text


async def run_gemini_final(analysis: AnalysisJson) -> PulseFinalJson:
    """Two-step pipeline call site #2 — Gemini only; no raw reviews."""
    api_key = pulse_config.get_gemini_api_key()
    if not api_key:
        raise PulsePipelineError("GEMINI_API_KEY is not set.")
    model = pulse_config.get_gemini_model()
    analysis_dict = analysis.model_dump(mode="json")
    prompt = build_gemini_user_prompt(analysis_dict)

    async def _once() -> PulseFinalJson:
        raw = await asyncio.to_thread(
            _gemini_generate_sync,
            prompt,
            model,
            api_key,
        )
        try:
            obj = extract_json_object(raw)
            return PulseFinalJson.model_validate(obj)
        except Exception as e:
            logger.exception("Gemini JSON parse/validate failed")
            raise PulsePipelineError(f"Gemini output invalid: {e}") from e

    from app.pulse.retry_util import retry_async

    try:
        return await retry_async(
            _once,
            retries=pulse_config.get_llm_max_retries(),
            backoff_sec=pulse_config.get_llm_retry_backoff_sec(),
            label="gemini",
        )
    except Exception as e:
        try:
            from google.api_core import exceptions as google_exc
        except ImportError:
            google_exc = None  # type: ignore[assignment]
        if google_exc and isinstance(e, google_exc.ResourceExhausted):
            raise PulsePipelineError(
                "Gemini quota or rate limit (429). Wait ~1 minute, try another GEMINI_MODEL "
                "(e.g. gemini-3.1-flash-lite-preview, gemini-2.0-flash), and check AI Studio quotas."
            ) from e
        if google_exc and isinstance(e, google_exc.NotFound):
            raise PulsePipelineError(
                f"Gemini model not found (404): {model!r} is not valid for generateContent. "
                "Set GEMINI_MODEL to an id from https://ai.google.dev/gemini-api/docs/models "
                "(e.g. gemini-3.1-flash-lite-preview, gemini-2.0-flash, gemini-1.5-flash)."
            ) from e
        raise
