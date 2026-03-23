# Dev log — Weekly Product Pulse & Fee Explainer

Short session notes (what we built, what we learned). Update at **end of session** or after a major feature — per `Brain.md`.

---

## Sessions

| Date | Notes |
|------|--------|
| *(Phase 0)* | Planning docs + repo hygiene: `.gitignore`, **`apps/backend/`** + **`apps/frontend/`** placeholders, **`Phase-0-Plan-Docs/`** (`PHASES.md`, exit criteria, `README.md`), `PHASE-FOLDERS.md`, `DEVLOG.md`. |
| 2026-03-17 | **Phase 1**: FastAPI health + CORS + pytest; Next.js routes + Footer + Jest; `.env.example` files; `npm run build` + tests green. No API keys required for this phase. |
| 2026-03-17 | **Phase 2**: `reviews_master.csv` + metadata; `google-play-scraper` + merge by `review_id`; APScheduler 48h fetch-only; `GET/POST /api/reviews/*`; Admin status UI + Jest; pytest (mocked fetch). No Play Store keys; default app id `in.indwealth`. |
| 2026-03-23 | **Phase 8 UI polish**: Reviews data + **Generate Preview** side-by-side; readable UTC timestamps; Weekly Pulse preview pane (beige); footer deploy stamp (“Last deployed on”) + centered System Design accordion. Footer stamp: update **`apps/frontend/lib/siteMeta.ts`** on each deploy (see **`DEVLOG.md`**). |
| 2026-03-23 | **Pre-Phase 9 hardening:** Restart/port hygiene docs, health diagnostics (`email_format_version` + header), meaningful-review quality filters, native Play Store ID pre-dedupe, fetch decision metadata + new endpoint **`GET /api/reviews/decision`**, tests updated and passing. |
| 2026-03-24 | **Phase 9 complete:** Deployed backend on Render (`indmoney-pulse-api.onrender.com`), frontend on Vercel, configured protected 48h external fetch via GitHub Actions cron, removed free-tier-only UI workarounds, and completed submission checklist/docs sync. |

---

*Add rows as you implement Phases 1–9.*
