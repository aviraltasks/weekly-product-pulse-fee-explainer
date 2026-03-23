# Development Plan — Weekly Product Pulse & Fee Explainer

**Purpose:** **Phase-level** checklist — what to build **in order**. One source of truth for “which phase are we in?”  

**Not the same as `TODO.md`:** Use **`TODO.md`** for **small, next-session tasks** (e.g. “fix CORS”, “add env var to README”). Use **this file** for **Phase 0 → Phase 9** completion.

**Full detail per phase:** See `ARCHITECTURE.md` §5.

**Note:** The “Done” column uses Markdown `[x]` / `[ ]` (not emoji) so editors don’t strip marks on save. If ticks disappear again, disable **Format on Save** for Markdown or see `.vscode/settings.json`.

---

## Phase checklist

| Phase | Name | Done |
|-------|------|------|
| 0 | Plan & documentation | [x] |
| 1 | Repository & runtime skeleton | [x] |
| 2 | Reviews data layer & scheduled fetch (48h) | [x] |
| 3 | Dual LLM pulse engine (Groq + Gemini) | [x] |
| 4 | Fee explainer (Exit Load) | [x] |
| 5 | Preview package (doc + email shape + As on) | [x] |
| 6 | MCP #1: Google Doc append | [x] |
| 7 | Subscribers store & MCP #2: Gmail send | [x] |
| 8 | Admin & subscriber UI + global footer | [x] |
| 9 | Deploy, resilience polish, submission artifacts | [ ] |

---

## Phase 0 exit criteria (before Phase 1 code) — **COMPLETE**

- [x] `ARCHITECTURE.md` reviewed and accepted
- [x] `ASSIGNMENT_BRIEF.md` aligned with brief (course deliverables)
- [x] `DEVELOPMENT_PLAN.md` (this file) created
- [x] `HEALTH.md` template in place (updated as pipelines run)
- [x] `TODO.md` created or updated for first implementation session
- [x] `.gitignore` excludes `.env` and secrets
- [x] Folder layout for **`apps/backend/`** + **`apps/frontend/`** agreed (see `apps/README.md`, `PHASE-FOLDERS.md`)

---

*Update checkboxes as phases complete. Append a one-line note to `CHANGELOG.md` when a phase finishes.*
