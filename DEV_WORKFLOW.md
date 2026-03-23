# Dev workflow — URLs, reload, avoiding “wrong process” issues

Use this with **`README.md`** (run commands) and **`HEALTH.md`** (ops checks).

---

## URLs to test the UI and trigger email (local)

| What | URL |
|------|-----|
| **Home** | [http://localhost:3000](http://localhost:3000) |
| **Admin — Create preview, Append to Doc, Send email** | **[http://localhost:3000/admin](http://localhost:3000/admin)** |
| **API health (verify `email_format_version`)** | [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health) |
| **Fetch decision (run/skip signal)** | [http://127.0.0.1:8000/api/reviews/decision](http://127.0.0.1:8000/api/reviews/decision) |

**Requirement:** backend on **:8000** + frontend on **:3000**, with **`apps/frontend/.env.local`** → `NEXT_PUBLIC_API_URL` pointing at the same API (e.g. `http://127.0.0.1:8000`). After changing env, restart **`npm run dev`**.

---

## Reload after code changes (full stack)

1. **Backend** — In the uvicorn terminal: **Ctrl+C**, then from repo root **`.\scripts\restart-backend.ps1`** (or **`apps\backend\.\restart-backend.ps1`**).  
   - Do **not** start a second uvicorn on **8000**; the restart script **refuses** if the port is busy (see below).
2. **Frontend** — In the Next terminal: **Ctrl+C**, then **`cd apps/frontend`** → **`npm run dev`**.  
   - Only **one** `next dev` on **3000** (see **`apps/frontend/README.md`** → Troubleshooting if chunks error).

---

## Prevent recurrence: ports, stale processes, and “wrong” API

| Problem | Cause | Prevention |
|--------|--------|------------|
| `/api/health` shows only `{"status":"ok"}` or missing `email_format_version` | Another program (or old uvicorn) bound to **8000** | **One** listener on **8000**: stop the old server (**Ctrl+C**) before restart; use **`.\scripts\restart-backend.ps1`** — it exits if **8000** is taken and prints PIDs. |
| `Stop-Process` says PID not found | Race: PID vanished between `Get-NetTCPConnection` and kill | Prefer **Ctrl+C** in the **uvicorn** terminal. **`uvicorn --reload`** uses two Python processes; killing one PID can confuse — stopping the terminal is cleanest. |
| Admin preview/email looks like old template | Browser cache **or** API not this repo’s code | Restart backend from **`apps/backend`** via script; confirm health JSON + **`X-Email-Format-Version: 2`** header; hard-refresh admin (**Ctrl+Shift+R**). |
| Two terminals both run `uvicorn` | Copy-paste commands | **One** backend process for local dev. Second bind fails or steals traffic — avoid. |
| Frontend calls wrong API | `NEXT_PUBLIC_API_URL` wrong or not restarted | Set **`apps/frontend/.env.local`**, restart **`npm run dev`**. |

---

## Scheduler (APScheduler) and “single backend”

The **48h reviews fetch** runs **inside** the FastAPI process (`app/main.py` lifespan).  

- **Implication:** Only **one** local **uvicorn** should run. A second backend (or another project on **8000**) duplicates risk: wrong CSV, wrong health, or confusing logs — not necessarily two schedulers if the second never starts, but **port conflicts** and **wrong listener** will still bite you.  
- **Config:** `SCHEDULER_ENABLED`, interval — see **`apps/backend/.env.example`** and reviews config.

If you change scheduler behavior, update **`README.md`** / **`ARCHITECTURE.md`** as needed and a line in **`DEVLOG.md`** when you ship.

---

## Docs / config — keep in sync when you change behavior

| Change | Update |
|--------|--------|
| New env vars, ports, URLs | **`README.md`**, **`apps/backend/.env.example`**, **`apps/frontend/.env.example`** |
| Health / ops expectations | **`HEALTH.md`** |
| Phase / milestone status | **`DEVELOPMENT_PLAN.md`**, **`DEVLOG.md`** |
| API or UI routes | **`ARCHITECTURE.md`**, frontend **`README.md`** |

**Rule of thumb:** one **authoritative** command path for backend restart (**`scripts/restart-backend.ps1`**) and one for frontend (**`npm run dev`** from **`apps/frontend`**). Link to them from **`README.md`** instead of duplicating long command blocks in many files.

---

## Quick verification commands (Windows PowerShell)

```powershell
# Who owns port 8000?
Get-NetTCPConnection -LocalPort 8000 -State Listen | Select-Object OwningProcess, LocalAddress

# Raw health body + header (this repo returns email_format_version + X-Email-Format-Version)
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -UseBasicParsing).Content
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -UseBasicParsing).Headers["X-Email-Format-Version"]
```

---

## Robustness, next phase, and deploy (why production is usually safer)

**If everything works locally now**, you’re in good shape. The painful issues we hit (**port 8000 busy**, **two `next dev`**, **wrong API on health**) are mostly **local dev hygiene** — many **do not recur the same way in deploy**.

| Local gotcha | Typical deploy behavior |
|--------------|-------------------------|
| Two apps fighting for **8000** / **3000** | One **container/process** per service; the host or platform maps **one** HTTP port per service (e.g. Render/Fly/Vercel). No “forgotten second uvicorn” unless you misconfigure **multiple** backends behind the same URL. |
| Stale `/api/health` body | **Wrong listener** on localhost. In prod, traffic goes to **your** deployed API URL only if DNS/env are correct. |
| `NEXT_PUBLIC_API_URL` mismatch | **Build-time** on Vercel: set env in the dashboard and **rebuild**. Backend: set **`FRONTEND_ORIGIN`** (or equivalent CORS) to your real frontend origin. |

### Before you move to **Phase 9** (deploy & polish)

Use this as a **gate** — not every item must be automated on day one, but you should **have checked** them:

1. **Backend:** `cd apps/backend` → `python -m pytest tests/ -q` passes on a clean machine / CI.
2. **Frontend:** `cd apps/frontend` → `npm test` + `npm run build` succeed.
3. **Env:** `apps/backend/.env.example` and `apps/frontend/.env.example` list **every** variable needed for prod (no secrets committed — placeholders only).
4. **Health:** Deployed API’s **`GET /api/health`** returns **`email_format_version`** + **`X-Email-Format-Version`**; platform uses the same path for **health checks** if you configure one.
5. **CORS:** Backend `FRONTEND_ORIGIN` (or your CORS allowlist) matches the **real** frontend URL (scheme + host, no trailing slash surprises).
6. **Scheduler:** If you run **multiple** API replicas, **either** run the 48h job on **one** instance only **or** use an external scheduler / `SCHEDULER_ENABLED=false` on extra replicas — otherwise you can duplicate fetches. Single-instance deploy is simplest for Milestone 2.

### “Everything is working OK?” — quick ongoing checks

- After meaningful changes: run **pytest** + **frontend build** (or CI when you add it).
- Before demo: **`DEV_WORKFLOW.md`** URLs + **`HEALTH.md`** table + a line in **`DEVLOG.md`**.
- Optional: add **GitHub Actions** (or similar) to run `pytest` + `npm run build` on every push — catches regressions before deploy.

---

*See also: **`HEALTH.md`** (verify `/api/health`), **`apps/frontend/README.md`** (port 3000 / `.next` issues).*
