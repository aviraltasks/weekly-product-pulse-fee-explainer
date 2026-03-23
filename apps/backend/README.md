# Backend API (`apps/backend`)

**Phases 2–5:** Reviews CSV + 48h fetch → dual LLM pulse → fee explainer → **Create Preview** (Weekly Pulse **N**, As on, doc + email payload).

**Stack:** Python + FastAPI, `google-play-scraper`, APScheduler, Groq + Gemini (pulse).

## Run

```powershell
cd apps/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Liveness |
| GET | `/api/reviews/status` | Row count, last refresh, scheduler flags |
| POST | `/api/reviews/fetch` | Run one fetch → merge into CSV (same as scheduler job) |
| POST | `/api/pulse/generate` | Pulse only (LLM1 + LLM2 + optional fee) |
| GET | `/api/fee` | Cached fee explainer (requires fee URLs or defaults) |
| POST | `/api/fee/refresh` | Re-scrape fee Source 1 |
| POST | `/api/preview/create` | **Create Preview** — increments **N**, returns `doc_append`, `email`, `doc_block_plain` |

## Data & env

- Default data dir: **`data/`** under this folder (`reviews_master.csv`, `reviews_metadata.json`, `weekly_pulse_counter.json`, fee cache files).
- Override with **`REVIEWS_DATA_DIR`** (absolute path recommended in production).
- See **`.env.example`** for `PLAY_STORE_APP_ID` (default **`in.indwealth`**), `PLAY_FETCH_MAX_REVIEWS`, `FETCH_INTERVAL_HOURS`, `SCHEDULER_ENABLED`, etc.

**LLM keys** (`GROQ_API_KEY`, `GEMINI_API_KEY`) are required for **`/api/pulse/generate`** and **`/api/preview/create`**. Gmail / Google Docs are **Phase 6+**.

## Tests

```powershell
python -m pytest tests/ -q
```

`tests/conftest.py` sets **`SCHEDULER_ENABLED=false`** so pytest does not start background jobs.

## Layout

```
apps/backend/
  app/
    main.py          # FastAPI + scheduler lifespan
    reviews/         # CSV, scraper, fetch service, router
    pulse/           # Phase 3+
    fee/
    integrations/
    subscribers/
  data/              # default REVIEWS_DATA_DIR (gitignored CSV optional)
  tests/
```
