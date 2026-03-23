"""Orchestrate sample → Groq → Gemini (two HTTP-style calls, sequential)."""

from __future__ import annotations

import logging

from app.pulse import config as pulse_config
from app.pulse.errors import PulsePipelineError
from app.pulse.gemini_final import run_gemini_final
from app.pulse.groq_analysis import run_groq_analysis
from app.pulse.sample_reviews import load_sample_for_pulse
from app.fee.service import get_fee_explainer_or_none
from app.pulse.schemas import (
    PulseGenerateMeta,
    PulseGenerateResponse,
    clamp_note_to_max_words,
    count_words,
    utc_now_iso,
)
from app.reviews import config as reviews_config

logger = logging.getLogger(__name__)


async def generate_pulse() -> PulseGenerateResponse:
    """
    Full Phase 3 pipeline: CSV sample → LLM1 (Groq) → LLM2 (Gemini).
    LLM2 never receives raw reviews.
    """
    csv_path = reviews_config.get_csv_path()
    max_n = pulse_config.get_pulse_sample_max()
    trunc = pulse_config.get_pulse_truncate_chars()

    samples = load_sample_for_pulse(
        csv_path,
        max_reviews=max_n,
        truncate_chars=trunc,
    )
    if not samples:
        raise PulsePipelineError(
            "No reviews in CSV. Run POST /api/reviews/fetch first (or wait for the scheduler).",
        )

    if not pulse_config.llm_keys_configured():
        raise PulsePipelineError(
            "Set GROQ_API_KEY and GEMINI_API_KEY in the environment (see .env.example).",
        )

    logger.info("Pulse: sampled %s reviews for Groq", len(samples))
    analysis = await run_groq_analysis(samples)
    logger.info("Pulse: Groq OK; calling Gemini (analysis only, no raw reviews)")
    final = await run_gemini_final(analysis)

    note, _truncated = clamp_note_to_max_words(final.weekly_note, max_words=250)
    wc = count_words(note)

    meta = PulseGenerateMeta(
        reviews_sampled=len(samples),
        groq_model=pulse_config.get_groq_model(),
        gemini_model=pulse_config.get_gemini_model(),
        generated_at_iso=utc_now_iso(),
        note_word_count=wc,
    )
    fee = get_fee_explainer_or_none()
    return PulseGenerateResponse(
        analysis=analysis,
        weekly_note=note,
        actions=list(final.actions),
        meta=meta,
        fee=fee,
    )
