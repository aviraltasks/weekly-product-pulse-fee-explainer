"""Google Doc append service (mocked API)."""

from __future__ import annotations

from unittest.mock import MagicMock

from app.integrations.google_doc.service import append_text_at_start, document_url


def test_document_url() -> None:
    assert "abc123" in document_url("abc123")
    assert "docs.google.com" in document_url("abc123")


def test_append_text_at_start_calls_batch_update() -> None:
    mock_svc = MagicMock()
    mock_docs = MagicMock()
    mock_svc.documents.return_value = mock_docs
    mock_docs.batchUpdate.return_value.execute.return_value = {"replies": []}

    out = append_text_at_start(document_id="doc1", text="Hello block", service=mock_svc)

    assert out["document_id"] == "doc1"
    assert out["inserted_char_count"] >= len("Hello block")
    mock_docs.batchUpdate.assert_called_once()
    call_kw = mock_docs.batchUpdate.call_args
    assert call_kw[1]["documentId"] == "doc1"
    body = call_kw[1]["body"]
    assert "requests" in body
    assert body["requests"][0]["insertText"]["location"]["index"] == 1
