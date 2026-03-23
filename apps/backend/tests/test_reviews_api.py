"""Reviews API + mocked Play Store fetch."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def reviews_data_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("REVIEWS_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("CRON_TRIGGER_TOKEN", "test-token")
    return tmp_path


@pytest.fixture
def client_reviews_dir(reviews_data_dir):
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_status_empty(client_reviews_dir) -> None:
    r = client_reviews_dir.get("/api/reviews/status")
    assert r.status_code == 200
    body = r.json()
    assert body["review_count"] == 0
    assert body["play_store_app_id"]
    assert body["fetch_interval_hours"] >= 1
    assert body["last_fetched_count"] == 0
    assert body["last_meaningful_count"] == 0


def test_status_with_csv_row(reviews_data_dir, client_reviews_dir) -> None:
    from app.reviews import config, csv_store

    assert config.get_data_dir() == reviews_data_dir
    csv_store.merge_new_reviews(
        config.get_csv_path(),
        [
            {
                "review_id": "r1",
                "user_name": "u",
                "content": "hello world this is long",
                "score": "5",
                "review_created_version": "",
                "at_iso": "2025-01-01T00:00:00+00:00",
                "thumbs_up": "0",
                "reply_content": "",
                "replied_at_iso": "",
                "app_version": "",
                "fetched_at_iso": "2025-01-02T00:00:00+00:00",
            }
        ],
    )
    r = client_reviews_dir.get("/api/reviews/status")
    assert r.json()["review_count"] == 1


def test_decision_endpoint_empty(client_reviews_dir) -> None:
    r = client_reviews_dir.get("/api/reviews/decision")
    assert r.status_code == 200
    body = r.json()
    assert body["decision"] is None
    assert body["meaningful_new_reviews"] == 0
    assert body["should_run_pulse"] is False
    assert body["min_meaningful_for_pulse"] >= 1


@patch(
    "app.reviews.service.play_fetch.fetch_reviews_sync",
    return_value=[
        {
            "reviewId": "mock-1",
            "userName": "Tester",
            "content": "Mocked review content is long enough for min length.",
            "score": 5,
            "reviewCreatedVersion": "1",
            "at": datetime.now(timezone.utc),
            "thumbsUpCount": 0,
            "replyContent": None,
            "repliedAt": None,
            "appVersion": "1.0",
        }
    ],
)
def test_fetch_merges_row(mock_fetch, client_reviews_dir) -> None:
    r = client_reviews_dir.post("/api/reviews/fetch", headers={"X-Cron-Token": "test-token"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["review_count"] == 1
    assert body["last_added_count"] == 1
    assert body["last_fetched_count"] == 1
    assert body["last_duplicate_count"] == 0
    assert body["last_filtered_count"] == 0
    assert body["last_meaningful_count"] == 1
    assert body["last_decision"] == "skip_low_signal"


@patch(
    "app.reviews.service.play_fetch.fetch_reviews_sync",
    return_value=[
        {
            "reviewId": "mock-1",
            "userName": "Tester",
            "content": "Mocked review content is long enough for min length.",
            "score": 5,
            "reviewCreatedVersion": "1",
            "at": datetime.now(timezone.utc),
            "thumbsUpCount": 0,
            "replyContent": None,
            "repliedAt": None,
            "appVersion": "1.0",
        }
    ],
)
def test_fetch_second_call_zero_added(mock_fetch, client_reviews_dir) -> None:
    client_reviews_dir.post("/api/reviews/fetch", headers={"X-Cron-Token": "test-token"})
    r2 = client_reviews_dir.post("/api/reviews/fetch", headers={"X-Cron-Token": "test-token"})
    assert r2.json()["review_count"] == 1
    assert r2.json()["last_added_count"] == 0
    assert r2.json()["last_duplicate_count"] == 1
    assert r2.json()["last_decision"] == "skip_no_new"


@patch(
    "app.reviews.service.play_fetch.fetch_reviews_sync",
    return_value=[
        {
            "reviewId": "mock-2",
            "userName": "Tester",
            "content": "Great app for tracking SIP and portfolio goals daily.",
            "score": 5,
            "reviewCreatedVersion": "1",
            "at": datetime.now(timezone.utc),
            "thumbsUpCount": 1,
            "replyContent": None,
            "repliedAt": None,
            "appVersion": "1.0",
        }
    ],
)
def test_decision_endpoint_after_fetch(mock_fetch, client_reviews_dir) -> None:
    client_reviews_dir.post("/api/reviews/fetch", headers={"X-Cron-Token": "test-token"})
    r = client_reviews_dir.get("/api/reviews/decision")
    assert r.status_code == 200
    body = r.json()
    assert body["decision"] == "skip_low_signal"
    assert body["meaningful_new_reviews"] == 1
    assert body["should_run_pulse"] is False


def test_fetch_requires_valid_token(client_reviews_dir) -> None:
    missing = client_reviews_dir.post("/api/reviews/fetch")
    assert missing.status_code == 401
    bad = client_reviews_dir.post("/api/reviews/fetch", headers={"X-Cron-Token": "wrong"})
    assert bad.status_code == 401
