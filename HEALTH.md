# Project Health — Weekly Product Pulse & Fee Explainer

**Purpose:** Lightweight log of **when critical pipelines last ran** and **whether they succeeded**.  
Update this **after major runs** or **end of session** (not on every keystroke).

**Audience:** You + anyone reviewing ops readiness (demo / redeploy).

---

## Latest status (fill as you go)

| Check | Last run (UTC or your TZ) | Status | Notes |
|-------|---------------------------|--------|--------|
| Backend `/api/health` | 2026-03-17 (dev) | ✅ OK | Phase 1+: `pytest` + `uvicorn` |
| Reviews fetch → `reviews_master.csv` | 2026-03-17 (dev) | ✅ OK | Phase 2: `POST /api/reviews/fetch` + pytest mocks |
| 48h scheduler (fetch only) | 2026-03-17 (dev) | ✅ OK | APScheduler when `SCHEDULER_ENABLED=true` |
| LLM1 (Groq) — analysis | | ☐ OK / ☐ Fail | |
| LLM2 (Gemini) — final pulse | | ☐ OK / ☐ Fail | |
| Fee explainer refresh / cache | | ☐ OK / ☐ Fail | |
| Google Doc append (MCP #1) | | ☐ OK / ☐ Fail | |
| Gmail send (MCP #2) | | ☐ OK / ☐ Fail | |
| Create Preview / **Weekly Pulse N** (last run) | | ☐ N/A / ☐ OK | Last N: |
| Frontend deploy (e.g. Vercel) | | ☐ N/A / ☐ OK | URL: |
| Backend deploy (e.g. Render/Fly) | | ☐ N/A / ☐ OK | URL: |

---

## Recent incidents (optional)

| Date | What broke | Fix / workaround |
|------|------------|------------------|
| | | |

---

## Verify `/api/health` locally (Windows)

For **URLs, full reload steps, port 8000/3000 discipline, scheduler note**, see **`DEV_WORKFLOW.md`**.

The JSON should include **`email_format_version`** (e.g. `"2"`), not only `"status":"ok"`.

If the body is only `{"status":"ok"}`, **another process is usually bound to port 8000** (not this repo’s uvicorn). Run `.\scripts\restart-backend.ps1` — it **refuses to start** if 8000 is taken; stop the PID it prints, then start again.

Confirm the real JSON body (and optional header):

```powershell
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -UseBasicParsing).Content
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -UseBasicParsing).Headers["X-Email-Format-Version"]
```

You should see `email_format_version` in the JSON and header `2`. Your **uvicorn** log line `Email template EMAIL_FORMAT_VERSION=2` matches this app’s template version.

---

## Environment sanity (optional checklist before demo)

- [ ] `GROQ_API_KEY` set on backend host
- [ ] `GEMINI_API_KEY` (or equivalent) set
- [ ] Gmail / Google credentials configured for send
- [ ] Google Doc ID + API credentials for append
- [ ] `CORS` / `FRONTEND_URL` correct for deployed frontend

---

*First created as template; replace placeholders as the project is implemented.*
