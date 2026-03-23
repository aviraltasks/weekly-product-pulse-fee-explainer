"""Request/response models for Doc append API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GoogleDocAppendRequest(BaseModel):
    """
    Body from admin UI: use `doc_block_plain` from `POST /api/preview/create`
    (exact preview text).
    """

    doc_block_plain: str = Field(..., min_length=1, max_length=500_000)


class GoogleDocAppendResponse(BaseModel):
    document_id: str
    document_url: str
    inserted_char_count: int
