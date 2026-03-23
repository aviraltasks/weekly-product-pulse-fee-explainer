"""FastAPI application entry."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.reviews import config as reviews_config
from app.reviews import service as reviews_service
from app.fee.router import router as fee_router
from app.integrations.gmail.router import router as gmail_router
from app.integrations.google_doc.router import router as google_doc_router
from app.preview.router import router as preview_router
from app.pulse.router import router as pulse_router
from app.preview.formatting import EMAIL_FORMAT_VERSION
from app.reviews.router import router as reviews_router
from app.subscribers.router import router as subscribers_router

# Load .env from apps/backend when present (local dev).
# override=True (default): .env wins over OS/shell (fixes stale GEMINI_MODEL in Windows env).
# Pytest sets DOTENV_NO_OVERRIDE=1 in conftest so .env does not override test env (e.g. SCHEDULER_ENABLED=false).
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.is_file():
    load_dotenv(_env_path, override=os.getenv("DOTENV_NO_OVERRIDE") != "1")

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)
logger.info("Loaded app.main from %s", Path(__file__).resolve())

_scheduler: AsyncIOScheduler | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler
    if reviews_config.scheduler_enabled():
        _scheduler = AsyncIOScheduler()

        async def _job() -> None:
            await reviews_service.run_fetch_cycle()

        _scheduler.add_job(
            _job,
            trigger=IntervalTrigger(hours=reviews_config.fetch_interval_hours()),
            id="reviews_fetch_interval",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        _scheduler.start()
        logger.info(
            "Reviews scheduler started: every %sh → CSV only",
            reviews_config.fetch_interval_hours(),
        )
    else:
        logger.info("Reviews scheduler disabled (SCHEDULER_ENABLED=false)")

    logger.info(
        "Email template EMAIL_FORMAT_VERSION=%s (POST /api/preview/create + /api/health)",
        EMAIL_FORMAT_VERSION,
    )

    yield

    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Reviews scheduler stopped")


app = FastAPI(
    title="Weekly Product Pulse API",
    version="0.7.0",
    description="INDmoney Play Store reviews → pulse + fee explainer (Milestone 2)",
    lifespan=lifespan,
)

_frontend = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[_frontend.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def api_health(response: Response) -> dict[str, str]:
    """Liveness check for deploy / monitoring."""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["X-Email-Format-Version"] = EMAIL_FORMAT_VERSION
    return {
        "email_format_version": EMAIL_FORMAT_VERSION,
        "status": "ok",
    }


app.include_router(reviews_router)
app.include_router(subscribers_router)
app.include_router(pulse_router)
app.include_router(fee_router)
app.include_router(preview_router)
app.include_router(google_doc_router)
app.include_router(gmail_router)
