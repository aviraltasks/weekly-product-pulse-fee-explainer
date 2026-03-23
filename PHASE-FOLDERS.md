# Phase artifact folders — naming convention

Each phase that produces a **dedicated folder** uses this pattern:

```text
Phase-<Number>-<ShortTitle>
```

- **`<Number>`** — Phase index (0–9).
- **`<ShortTitle>`** — **2–3 words**, Title-Case, hyphen-separated, describing what that phase is about (easy to scan in Explorer / Git).

**Examples:**

| Phase | Folder name | Short title meaning |
|-------|-------------|---------------------|
| 0 | `Phase-0-Plan-Docs` | Planning + documentation |
| 1 | `Phase-1-Runtime-Skeleton` *(planned)* | Backend + frontend shells |
| 2 | `Phase-2-Reviews-Data` *(planned)* | CSV + fetch + scheduler |

Add a row here when a phase folder is created.

### Where the **application code** lives (not inside `Phase-*`)

| | |
|--|--|
| **`apps/backend/`** | API service (FastAPI) — **deployable app**. |
| **`apps/frontend/`** | Web UI (Next.js) — **deployable app**. |
| **`apps/README.md`** | Explains that **`apps/`** = runnable products vs **`Phase-*`** = documentation only. |

**Why `apps/`?** Reviewers immediately see: *phase folders* = planning snapshots; *`apps/`* = real code. Same pattern as many monorepos (Nx, Turborepo, etc.).

| | |
|--|--|
| **Deploy** | Point Vercel → `apps/frontend/`, Render/Fly → `apps/backend/` (or repo root with `root` / `Dockerfile` set accordingly). |
| **Not under `Phase-1-…`** | Putting code only inside `Phase-1-Runtime-Skeleton/` breaks default build roots; that folder stays for **notes/screenshots** if needed. |

So: **`Phase-*`** = planning artifacts; **`apps/backend/` + `apps/frontend/`** = runnable services. Placeholders + READMEs until Phase 1 scaffolding.

---

*Created when `Phase-0-Plan-Docs` was introduced.*
