"""Fee explainer API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.fee.service import get_fee_explainer_or_none, refresh_fee_explainer

router = APIRouter(prefix="/api/fee", tags=["fee"])


@router.get("")
async def get_fee():
    block = get_fee_explainer_or_none()
    if block is None:
        raise HTTPException(
            status_code=503,
            detail="Fee explainer not configured: set FEE_SOURCE_URL_1 and FEE_SOURCE_URL_2",
        )
    return block.model_dump(mode="json")


@router.post("/refresh")
async def post_fee_refresh():
    try:
        block = await refresh_fee_explainer()
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    return block.model_dump(mode="json")
