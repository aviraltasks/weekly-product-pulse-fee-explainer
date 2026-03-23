"""POST /api/integrations/google-doc/append — Phase 6."""

from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, HTTPException
from googleapiclient.errors import HttpError

from app.integrations.google_doc.config import get_google_doc_id, google_doc_append_configured
from app.integrations.google_doc.schemas import GoogleDocAppendRequest, GoogleDocAppendResponse
from app.integrations.google_doc.service import append_preview_block, document_url

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/integrations/google-doc", tags=["integrations", "google-doc"])


@router.post("/append", response_model=GoogleDocAppendResponse)
async def post_google_doc_append(body: GoogleDocAppendRequest) -> GoogleDocAppendResponse:
    """
    Append the preview block to the configured Google Doc (newest at top).
    Requires `GOOGLE_DOC_ID` + `GOOGLE_SERVICE_ACCOUNT_FILE`; Doc must be shared with the SA email (Editor).
    """
    if not google_doc_append_configured():
        raise HTTPException(
            status_code=503,
            detail=(
                "Google Doc append not configured: set GOOGLE_DOC_ID and "
                "GOOGLE_SERVICE_ACCOUNT_FILE (see apps/backend/.env.example)"
            ),
        )
    doc_id = get_google_doc_id()

    try:
        result = await asyncio.to_thread(append_preview_block, body.doc_block_plain)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except OSError as e:
        logger.exception("Doc append I/O error")
        raise HTTPException(status_code=503, detail=str(e)) from e
    except HttpError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Google Docs API error: {getattr(e, 'reason', None) or str(e)}",
        ) from e
    except Exception as e:  # noqa: BLE001
        logger.exception("Doc append failed")
        raise HTTPException(status_code=500, detail=str(e)) from e

    return GoogleDocAppendResponse(
        document_id=doc_id,
        document_url=document_url(doc_id),
        inserted_char_count=int(result.get("inserted_char_count", 0)),
    )
