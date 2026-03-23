# Changelog — Weekly Product Pulse & Fee Explainer

All notable changes to this project are logged here (lightweight; per `Brain.md`, update after major features or phases).

---

## [Unreleased]

- **Phase 9 complete:** Production deploy live (Render backend + Vercel frontend), GitHub Actions 48h protected fetch automation enabled, and submission/docs checklists closed.
- **Docs:** Added `docs/GITHUB_ACTIONS_CRON_SETUP.md` — one-time GitHub Actions secrets and manual test for the 48h review fetch workflow.
- **Admin / footer:** Footer deploy stamp updated; **Automated fetch** label clarifies GitHub cron vs in-app scheduler; **`/admin`** uses `force-dynamic` so the admin UI isn’t served from a stale cached shell after deploy.
- **Deploy / ops (Starter):** `render.yaml` uses **`plan: starter`** (Gmail SMTP allowed). Removed free-tier-only **frontend GET retries** and **error substring remapping**; GitHub cron **health check** is a single `curl` (no long cold-start loop).
- **UI premium polish (home hero):** Replaced basic right-side placeholder with a restrained glass-style abstract dashboard card (muted metrics bars/dots/sparkline), then softened shadow for a quieter premium look.
- **Branding + footer text:** Header title updated to **INDmoney Feedback Pulse**; footer wording updated to **Last deployed on** (IST deploy stamp), and internal helper hints removed from user-facing UI.
- **Footer architecture panel:** Upgraded accordion to display the full architecture content from `apps/frontend/public/architecture-full.md` instead of a short inline summary.
- **Reviews fetch decisioning:** Added `GET /api/reviews/decision` for lightweight admin/pipeline gating (`skip_no_new` / `skip_low_signal` / `run_ready`) with counters and threshold context.
- **Ingestion robustness:** Pre-filter dedupe by native Play Store `reviewId` before normalization/merge; metadata now tracks fetched/duplicate/filtered/meaningful counts.
- **Meaningful review quality gate:** Added reusable filtering for analysis input (min length + min words, emoji/noise rejection, alphanumeric-junk rejection, English/Hindi-safe text).
- **Config knobs:** Added `REVIEW_MIN_MEANINGFUL_WORDS` and `MIN_MEANINGFUL_NEW_REVIEWS_FOR_PULSE` in backend config and `.env.example`.

- **Email (HTML + plain):** Centered body title `WEEKLY PRODUCT PULSE: [As on date]`; section labels **TOP 3 CUSTOMER THEMES**, **CUSTOMER VERBATIM QUOTES**, **EXECUTIVE ANALYSIS**, **PRIORITY ACTIONS**, **KNOWLEDGE BASE: FEE EXPLAINER**; `<hr>` + spacing before fee block; no pipeline logic changes.
- **Admin email preview:** Renders **`email.body_html`** in an **iframe** (same as sent multipart HTML); plain text in a nested disclosure — fixes “old format” in preview when only `body_plain` was shown in `<pre>`.
- **Email template diagnostics:** `email.format_version` + root **`email_template_version`** on `POST /api/preview/create` + **`GET /api/health`** → `email_format_version: "2"`; admin shows **API base URL** + health line; warns if not v2; **`scripts/restart-backend.ps1`** clears `__pycache__` and starts uvicorn from `apps/backend`; startup log prints `EMAIL_FORMAT_VERSION`.

### Phase 8 — Admin & subscriber UI (complete)

- **UI polish (2026-03-23):** **Reviews data** + **Generate Preview** side-by-side; **reviews stats** as labeled rows + formatted UTC (no raw ISO); Weekly Pulse pane **beige** + **Preview** badge; footer deploy stamp from **`lib/siteMeta.ts`**; **System Design** accordion **centered** under Built with Cursor.
- **Next.js:** Global **header** (Home / Subscribers / Admin), **editorial theme** (cream background, Playfair + DM Sans, minimal cards).
- **`/subscribers`:** **`SubscribeForm`** → **`POST /api/subscribers`** with validation feedback.
- **`/admin`:** **Create preview** (`POST /api/preview/create`), structured **preview pane**, **subscriber checkboxes** (default all) from **`GET /api/subscribers`**, **Append to Google Doc** and **Send email** (independent actions).
- **Footer** on every route via **`app/layout.tsx`** (§2.1).

- **Email newsletter:** preview `email` now includes **`body_html`** (bold **TOP 3**, **QUOTES**, **NOTE**, **ACTIONS**, **FEE**; bullet lists; no TL;DR). Gmail send uses **multipart** when **`body_html`** is posted with **`/api/integrations/gmail/send`**.

### Phase 7 — Subscribers store & Gmail send (MCP #2) (complete)

- **`POST /api/subscribers`**, **`GET /api/subscribers`** — JSON store (`SUBSCRIBERS_STORE_PATH` or default `data/subscribers.json`); dedupe by email (case-insensitive).
- **`POST /api/integrations/gmail/send`** — body `{ to_emails, subject, body_plain }` (from preview `email`); **Gmail SMTP** (`smtp.gmail.com:587`) with **`GMAIL_SMTP_USER`** + **`GMAIL_APP_PASSWORD`**; **`GMAIL_STRICT_RECIPIENTS`** (default true) limits sends to stored subscribers.
- **Deps:** `email-validator` for `EmailStr`. **Tests:** store, API, recipient filter, mocked SMTP.

### Phase 6 — Google Doc append (MCP #1) (complete)

- **`POST /api/integrations/google-doc/append`** — body `{ "doc_block_plain": "<from preview>" }`; inserts at **top** of doc (newest first); returns **`document_url`** for opening the Doc.
- **Auth:** Google **service account** JSON path via **`GOOGLE_SERVICE_ACCOUNT_FILE`**; target Doc **`GOOGLE_DOC_ID`**; enable **Google Docs API** in GCP; **share the Doc** with the service-account email (**Editor**).
- **Deps:** `google-api-python-client`, `google-auth`. **`doc_append.weekly_pulse_n`** added to preview JSON for traceability.
- **Tests:** mocked Docs client + API 503/200 paths.

### Phase 5 — Preview package (doc + email shape + As on) (complete)

- **`POST /api/preview/create`**: runs pulse + fee, increments persisted **Weekly Pulse N**, returns **`as_on`**, nested **`pulse`**, **`doc_append`** (MCP-ready fields), **`email`** (subject + body), **`doc_block_plain`**.
- **Data:** `weekly_pulse_counter.json` (configurable via **`WEEKLY_PULSE_COUNTER_PATH`**); display timezone **`PREVIEW_DISPLAY_TIMEZONE`** (default `Asia/Kolkata`).
- **Tests:** counter, formatting/serialization, API with mocked `generate_pulse`.

### Phase 4 — Fee explainer (exit load) (complete)

- **`GET /api/fee`**, **`POST /api/fee/refresh`**; cached JSON (`FEE_CACHE_PATH` or default under `data/`), bullets from **`data/fee_defaults.json`**, two official URLs via **`FEE_SOURCE_URL_1`** / **`FEE_SOURCE_URL_2`**.
- **`POST /api/pulse/generate`** response includes optional **`fee`** block when URLs are configured.

**Update (author sources):** Source 1 — scrape INDmoney FAQ (“What is the exit load of the fund?”) for SBI Large Cap tiers; Source 2 — **[SEBI investor — Exit load](https://investor.sebi.gov.in/exit_load.html)** summarized in **`data/fee_source2_hardcoded.json`** (not scraped). Default URLs in **`app/fee/config.py`** unless env overrides or disables (empty string).

### Phase 2 — Reviews data layer & scheduled fetch (48h) (complete)

- **`reviews_master.csv`** (and **`reviews_metadata.json`**) under configurable **`REVIEWS_DATA_DIR`** (default `apps/backend/data/`).
- **`google-play-scraper`**: fetch + normalize + **merge by `review_id`** (idempotent); filters by minimum content length.
- **APScheduler**: every **`FETCH_INTERVAL_HOURS`** (default **48**) runs fetch only — **no** Doc append or email.
- **API:** `GET /api/reviews/status`, `POST /api/reviews/fetch` (manual trigger / demo).
- **Admin UI:** `AdminReviewStatus` on `/admin` — counts, last refresh, **Refresh reviews now**.
- **Tests:** `test_clean`, `test_csv_store`, `test_reviews_api` (mocked fetch), `tests/conftest.py` sets **`SCHEDULER_ENABLED=false`**.

### Phase 1 — Repository & runtime skeleton (complete)

- **`apps/backend/`**: FastAPI app (`GET /api/health` → `{"status":"ok"}`), CORS from `FRONTEND_ORIGIN`, package placeholders (`reviews`, `pulse`, `fee`, `integrations`, `subscribers`), `requirements.txt` + `requirements-dev.txt`, pytest `tests/test_health.py` (TestClient).
- **`apps/frontend/`**: Next.js 14 App Router — `/`, `/subscribers`, `/admin` (placeholders), global `Footer` (author, LinkedIn, Built with Cursor, collapsible System Design), Jest + Testing Library `__tests__/Home.test.tsx`.
- **Env templates**: `apps/backend/.env.example` (`FRONTEND_ORIGIN`); `apps/frontend/.env.example` (`NEXT_PUBLIC_API_URL`).

### `apps/` layout

- Renamed root **`backend/`** and **`frontend/`** → **`apps/backend/`** and **`apps/frontend/`**, added **`apps/README.md`** so reviewers see **`apps/`** = runnable code vs **`Phase-*`** = planning docs.

### Repo hygiene

- Removed duplicate root **`PHASES.md`** — canonical phase index is **`Phase-0-Plan-Docs/PHASES.md`** only.
- **`PHASE-FOLDERS.md`**: documented why app code lives under **`apps/`** (not inside `Phase-*`); later refined to **`apps/backend/`** + **`apps/frontend/`** — see current file.

### Phase 0 folder

- Renamed **`phase-0/`** → **`Phase-0-Plan-Docs/`** (pattern `Phase-<n>-<ShortTitle>`). Added **`PHASE-FOLDERS.md`**. Root **`PHASES.md`** points to `Phase-0-Plan-Docs/PHASES.md`.

### Phase 0 — Plan & documentation (complete)

- Added **`.gitignore`** (env, Python, Node, OS cruft).
- Added **`backend/README.md`** and **`frontend/README.md`** (reserved layout; no app code yet).
- Added **`DEVLOG.md`** stub; **`PHASES.md`** quick index.
- Marked Phase **0** ✅ in **`DEVELOPMENT_PLAN.md`**; all Phase 0 exit criteria checked.

### Documentation (pre-implementation sync)

- Aligned all project `.md` files with latest decisions: dual LLM (Groq + Gemini), **Weekly Pulse N** on Create Preview, **Subscribers Enter** / **Admin Enter** UI, global footer + System Design accordion (closed by default), **48h** scheduler = fetch to CSV only (no auto-append/send), MCP **#1** Doc append / **#2** Gmail send, quotes **1 per top-3 theme**, low-review handling (§3.1), **no invented URLs** (author supplies fund/official links).
- Added: **`SYSTEM_OVERVIEW.md`**, **`CHANGELOG.md`**, **`README.md`** stub; updated **`ASSIGNMENT_BRIEF.md`** (MCP/email alignment, section D→E), **`Brain.md`**, **`DEVELOPMENT_PLAN.md`** Phase 0, **`HEALTH.md`**, **`TODO.md`**, **`SAMPLE_PULSE_OUTPUTS.md`** header, **`ARCHITECTURE.md`** §3.1 + Phase 3/5 detail.
- **`SAMPLE_PULSE_OUTPUTS.md`**: shortened leadership layout (TL;DR, compact sections); **§D** LLM token strategy; **~120–150 word** note target; **`ARCHITECTURE.md`** / **`ASSIGNMENT_BRIEF.md`** / **`SYSTEM_OVERVIEW.md`** aligned.

---

*Add dated entries as phases complete.*
