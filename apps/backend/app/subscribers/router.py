"""Subscriber signup + list (Phase 7)."""

from __future__ import annotations

from fastapi import APIRouter

from app.subscribers.schemas import SubscribeRequest, SubscriberRecord, SubscribersListResponse
from app.subscribers.store import add_subscriber, list_subscribers

router = APIRouter(prefix="/api", tags=["subscribers"])


@router.post("/subscribers", response_model=SubscriberRecord)
async def post_subscribe(body: SubscribeRequest) -> SubscriberRecord:
    row = add_subscriber(str(body.email))
    return SubscriberRecord(email=row["email"], subscribed_at_iso=row["subscribed_at_iso"])


@router.get("/subscribers", response_model=SubscribersListResponse)
async def get_subscribers() -> SubscribersListResponse:
    rows = list_subscribers()
    recs = [SubscriberRecord(email=r["email"], subscribed_at_iso=r["subscribed_at_iso"]) for r in rows]
    return SubscribersListResponse(subscribers=recs, count=len(recs))
