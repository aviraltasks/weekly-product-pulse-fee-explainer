# Frontend web app (`apps/frontend`)

**Stack:** Next.js 14 (App Router), deployable to Vercel. **API:** `NEXT_PUBLIC_API_URL` (default `http://localhost:8000` — see `.env.example`).

## Run

```powershell
cd apps/frontend
npm install
npm run dev
```

- **App:** `http://localhost:3000`
- **No API keys** in the browser — all LLM and integration secrets stay on the backend.

## Routes (Phase 8)

| Path | Screen |
|------|--------|
| `/` | Home — editorial hero + entry cards to Subscribers & Admin |
| `/subscribers` | Email subscribe → `POST /api/subscribers` |
| `/admin` | Reviews status + refresh; **Create preview**; preview pane; subscriber checkboxes; **Append to Google Doc**; **Send email** |

**Layout:** **Site header** on all pages; **global footer** (§2.1 in `ARCHITECTURE.md`) — last updated, author, LinkedIn, Built with Cursor, collapsible System Design.

**Deploy stamp:** Update **`lib/siteMeta.ts`** (`SITE_LAST_UPDATED`, `SITE_LAST_UPDATED_ISO`) when you ship — and add a row to repo-root **`DEVLOG.md`**.

## Tests & build

```powershell
npm test
npm run build
```

## Troubleshooting (dev server / white screen / refresh loop)

**Symptoms:** `Cannot find module './682.js'` (or similar numbered chunk), page **keeps reloading**, or the Next error overlay won’t go away.

**Cause:** The **`.next`** dev bundle got out of sync with the running **`next dev`** process (HMR). The client keeps asking for old chunk files → error → Fast Refresh retries → **looks like an infinite refresh**.

**Fix (do these in order):**

1. **Stop every** dev server: in **all** terminals, **Ctrl+C** (only one `next dev` should run on port 3000).
2. **Optional:** Task Manager → end extra **Node.js** processes if something is still bound to port 3000.
3. From **`apps/frontend`** run a **clean start**:

```powershell
cd apps/frontend
npm run dev:clean
```

That deletes **`.next`** (and **`node_modules/.cache`** if present), then starts dev. **Do not** delete files inside `.next` while `npm run dev` is running.

**Code-side hardening (already in repo):** root layout wraps **`SiteHeader`** in **`<Suspense>`** (required when using **`usePathname()`** in the App Router). **`next.config.mjs`** disables webpack’s persistent cache **in development only** to reduce stale chunk IDs on Windows.

If errors persist after a clean start, temporarily exclude **`apps/frontend/.next`** from real-time antivirus scanning.

## Theme

Warm off-white background, **Playfair Display** headlines, **DM Sans** body, black primary buttons, muted brown accent (`#A68966`) — editorial / minimal; no stock images required.
