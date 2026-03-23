"""HTTP routes for pulse generation (Phase 3)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.pulse.errors import PulsePipelineError
from app.pulse.pipeline import generate_pulse
from app.pulse.schemas import PulseGenerateResponse

router = APIRouter(prefix="/api/pulse", tags=["pulse"])


@router.post("/generate", response_model=PulseGenerateResponse)
async def post_pulse_generate() -> PulseGenerateResponse:
    """
    Run LLM1 (Groq) then LLM2 (Gemini). Requires reviews in CSV + API keys.
    """
    try:
        return await generate_pulse()
    except PulsePipelineError as e:
        msg = str(e)
        code = 400
        if "GROQ_API_KEY" in msg or "GEMINI_API_KEY" in msg or "Set GROQ" in msg:
            code = 503
        raise HTTPException(status_code=code, detail=msg) from e
