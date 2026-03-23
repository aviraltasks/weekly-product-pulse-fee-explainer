"""Preview API — Create Preview (Phase 5)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.pulse.errors import PulsePipelineError
from app.preview.schemas import PreviewCreateResponse
from app.preview.service import create_preview

router = APIRouter(prefix="/api/preview", tags=["preview"])


@router.post("/create", response_model=PreviewCreateResponse)
async def post_preview_create() -> PreviewCreateResponse:
    """
    Run pulse + fee, assign next Weekly Pulse N, return Doc + email shapes for admin UI.
    """
    try:
        return await create_preview()
    except PulsePipelineError as e:
        msg = str(e)
        code = 400
        if "GROQ_API_KEY" in msg or "GEMINI_API_KEY" in msg or "Set GROQ" in msg:
            code = 503
        raise HTTPException(status_code=code, detail=msg) from e
