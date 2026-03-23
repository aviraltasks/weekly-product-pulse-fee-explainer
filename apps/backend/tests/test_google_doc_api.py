"""POST /api/integrations/google-doc/append."""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient


def test_google_doc_append_503_when_not_configured(monkeypatch) -> None:
    monkeypatch.delenv("GOOGLE_DOC_ID", raising=False)
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_FILE", raising=False)
    from app.main import app

    with TestClient(app) as client:
        r = client.post(
            "/api/integrations/google-doc/append",
            json={"doc_block_plain": "Some preview text\n\n"},
        )
    assert r.status_code == 503


def test_google_doc_append_200_when_mocked(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GOOGLE_DOC_ID", "test-doc-id-xyz")
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(tmp_path / "dummy.json"))
    (tmp_path / "dummy.json").write_text("{}", encoding="utf-8")

    def _fake_append(text: str) -> dict:
        return {"document_id": "test-doc-id-xyz", "inserted_char_count": len(text) + 2}

    from app.main import app

    with patch(
        "app.integrations.google_doc.router.append_preview_block",
        side_effect=_fake_append,
    ):
        with TestClient(app) as client:
            r = client.post(
                "/api/integrations/google-doc/append",
                json={"doc_block_plain": "Block A"},
            )
    assert r.status_code == 200
    data = r.json()
    assert data["document_id"] == "test-doc-id-xyz"
    assert "docs.google.com" in data["document_url"]
    assert data["inserted_char_count"] > 0
