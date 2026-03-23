"""Lightweight retry with exponential backoff (LLM HTTP calls)."""

from __future__ import annotations

import asyncio
import logging
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def retry_async(
    op: Callable[[], Awaitable[T]],
    *,
    retries: int,
    backoff_sec: float,
    label: str,
) -> T:
    last: BaseException | None = None
    for attempt in range(retries):
        try:
            return await op()
        except Exception as e:
            last = e
            if attempt >= retries - 1:
                logger.warning("%s failed after %s attempts: %s", label, retries, e)
                raise
            delay = backoff_sec * (2**attempt) + random.uniform(0, 0.25)
            logger.info("%s retry %s/%s in %.2fs: %s", label, attempt + 1, retries, delay, e)
            await asyncio.sleep(delay)
    assert last is not None
    raise last
