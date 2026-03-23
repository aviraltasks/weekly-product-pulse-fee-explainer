# Weekly Product Pulse and Fee Explainer

**Status:** **Phase 8 complete** — web UI: subscribers signup, admin **Create preview** / **Append to Doc** / **Send email** + global footer. Next: **Phase 9** — deploy & submission polish — see **`DEVELOPMENT_PLAN.md`**.

## App URL (try the product)

| Environment | URL |
|---------------|-----|
| **Local (full stack)** | **[http://localhost:3000](http://localhost:3000)** — start backend `:8000` + frontend `:3000` (see below). |
| **Production** | *Not set yet — after Phase 9 deploy, paste your Vercel (frontend) + API URL here.* |

**Single URL to test everything in the browser:** **http://localhost:3000**

**Test UI + trigger email (local):** open **[http://localhost:3000/admin](http://localhost:3000/admin)** — **Create preview**, then **Send email** (backend **:8000** + frontend **:3000** must both be running). Full reload / port pitfalls → **`DEV_WORKFLOW.md`**.

If `/admin` shows a Next.js error about a missing **`./777.js`** (or similar), delete **`apps/frontend/.next`** and run **`npm run dev:clean`** — see **`apps/frontend/README.md`** → Troubleshooting.

## Run locally

### Backend (FastAPI)

```powershell
cd apps/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
# Optional: copy .env.example to .env (Play Store app id, scheduler, data dir)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Health: `GET http://localhost:8000/api/health` → `{"status":"ok","email_format_version":"2"}` (if `email_format_version` is missing or not `"2"`, the API is running **old code** — restart uvicorn from `apps/backend` and clear `app/preview/__pycache__` if email labels look wrong in the admin preview or Gmail)
- **Reliable backend restart (Windows):** `.\scripts\restart-backend.ps1` from **repo root**, **or** `.\restart-backend.ps1` from **`apps/backend`** (wrapper to the same script) — clears `apps/backend/app/**/__pycache__`, then runs uvicorn from **`apps/backend`** so imports always match this repo.
- Reviews status: `GET http://localhost:8000/api/reviews/status` (row count, last refresh, scheduler)
- Reviews decision: `GET http://localhost:8000/api/reviews/decision` (latest fetch decision: `skip_no_new` / `skip_low_signal` / `run_ready`)
- Manual fetch (protected): `POST http://localhost:8000/api/reviews/fetch` with `X-Cron-Token`
- Create preview (pulse + fee + **N**): `POST http://localhost:8000/api/preview/create` (requires reviews CSV + LLM keys; see `.env.example`)
- Data files (default): `apps/backend/data/reviews_master.csv`, `reviews_metadata.json`, `weekly_pulse_counter.json` (preview serial)
- Fetch quality + dedupe: native Play Store `reviewId` dedupe, meaningful-content filtering (emoji/noise guard), and fetch counters/decision persisted in metadata.
- Tests: `python -m pytest tests/ -q` (scheduler off in tests via `tests/conftest.py`)

### Frontend (Next.js)

```powershell
cd apps/frontend
npm install
# NEXT_PUBLIC_API_URL=http://localhost:8000 (see .env.example)
npm run dev
```

- App: `http://localhost:3000` — **Subscribers** (signup), **Admin** (preview, Doc append, email send), global footer — see **`apps/frontend/README.md`**.
- Tests: `npm test`
- Production build: `npm run build`

### Phase 2 — keys & URLs

- **No API keys** for Play Store scraping (public reviews via `google-play-scraper`).
- **Optional:** set **`PLAY_STORE_APP_ID`** if you track a different app than the default (**`in.indwealth`** — INDmoney listing). No passwords required for this phase.
- **Author-provided official/fund/regulator URLs** are for **fee explainer / sources** (Phase 4+), not for Phase 2.

## Quick links

| Document | Purpose |
|----------|---------|
| [`SYSTEM_OVERVIEW.md`](SYSTEM_OVERVIEW.md) | What we’re building (short) |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Phases, tech decisions, pulse logic (§3.1), footer |
| [`ASSIGNMENT_BRIEF.md`](ASSIGNMENT_BRIEF.md) | Course rubric + submission checklist |
| [`SAMPLE_PULSE_OUTPUTS.md`](SAMPLE_PULSE_OUTPUTS.md) | Mock Google Doc + email (`Weekly Pulse N`) |
| [`DEVELOPMENT_PLAN.md`](DEVELOPMENT_PLAN.md) | Phase 0–9 checklist (Phase 0–8 ✅; Phase 9 pending) |
| [`Phase-0-Plan-Docs/PHASES.md`](Phase-0-Plan-Docs/PHASES.md) | One-line phase index |
| [`Phase-0-Plan-Docs/README.md`](Phase-0-Plan-Docs/README.md) | Phase 0 — Plan & Docs |
| [`apps/README.md`](apps/README.md) | **`apps/`** = API + web; **`Phase-*`** = docs only |
| [`PHASE-FOLDERS.md`](PHASE-FOLDERS.md) | How phase folders are named |
| [`DEVLOG.md`](DEVLOG.md) | Session notes |
| [`DEV_WORKFLOW.md`](DEV_WORKFLOW.md) | **Local URLs, reload steps, avoid wrong process on :8000/:3000**, scheduler note, **§ robustness & Phase 9 deploy gate** |
| [`DEPLOY_AUTOMATION.md`](DEPLOY_AUTOMATION.md) | Render Blueprint + GitHub Actions cron/smoke setup |

When integrations land, this README will also cover: MCP approvals, fee scenario, and **author-provided** source list (4–6 URLs — no invented links).

---

*Project: Milestone 2 — INDmoney Play Store reviews → pulse + Exit Load explainer → Google Doc + Gmail.*
