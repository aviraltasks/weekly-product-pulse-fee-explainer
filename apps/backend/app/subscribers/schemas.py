"""Subscriber API models."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class SubscribeRequest(BaseModel):
    email: EmailStr


class SubscriberRecord(BaseModel):
    email: str
    subscribed_at_iso: str


class SubscribersListResponse(BaseModel):
    subscribers: list[SubscriberRecord]
    count: int
