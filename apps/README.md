# `apps/` — runnable applications

This folder holds **deployable code** (API + web UI). It is **not** the same as **`Phase-*`** folders, which hold **phase documentation and snapshots** only.

| Path | Role |
|------|------|
| **`backend/`** | FastAPI API — health at `/api/health`; see **`backend/README.md`** |
| **`frontend/`** | Next.js web app — see **`frontend/README.md`** |

Deploy tools (Vercel, Render, etc.) will point at these paths. **Do not** move app code into `Phase-1-...` — see **`PHASE-FOLDERS.md`**.

**Quick start:** Root **`README.md`** has copy-paste commands for `uvicorn` and `npm run dev`.
