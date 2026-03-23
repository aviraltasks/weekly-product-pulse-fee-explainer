"""Append plain text to the top of a Google Doc (newest-first)."""

from __future__ import annotations

import logging
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.integrations.google_doc.config import (
    load_service_account_info,
    get_google_doc_id,
)

logger = logging.getLogger(__name__)

SCOPES = ("https://www.googleapis.com/auth/documents",)


def build_docs_service() -> Any:
    info = load_service_account_info()
    creds = service_account.Credentials.from_service_account_info(
        info,
        scopes=SCOPES,
    )
    return build("docs", "v1", credentials=creds, cache_discovery=False)


def append_text_at_start(*, document_id: str, text: str, service: Any | None = None) -> dict[str, Any]:
    """
    Insert `text` at index 1 (top of body, newest block first per ARCHITECTURE.md).
    Caller may pass a pre-built `service` for testing (mock).
    """
    if service is None:
        service = build_docs_service()

    # Trailing newlines separate from previous content
    payload_text = text.rstrip() + "\n\n"
    body = {
        "requests": [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": payload_text,
                }
            }
        ]
    }
    try:
        result = (
            service.documents()
            .batchUpdate(documentId=document_id, body=body)
            .execute()
        )
    except HttpError as e:
        logger.warning("Google Docs batchUpdate failed: %s", e)
        raise
    return {
        "document_id": document_id,
        "replies": result.get("replies", []),
        "write_control": result.get("writeControl", {}),
        "inserted_char_count": len(payload_text),
    }


def append_preview_block(doc_block_plain: str, *, service: Any | None = None) -> dict[str, Any]:
    """Append using configured GOOGLE_DOC_ID."""
    doc_id = get_google_doc_id()
    if not doc_id:
        raise ValueError("GOOGLE_DOC_ID is not set")
    return append_text_at_start(document_id=doc_id, text=doc_block_plain, service=service)


def document_url(document_id: str) -> str:
    return f"https://docs.google.com/document/d/{document_id}/edit"
