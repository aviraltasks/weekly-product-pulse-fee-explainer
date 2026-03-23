# Weekly Product Pulse & Fee Explainer — Architecture

**Audience:** Product leaders, senior PMs, engineers, and you (learning).  
**Intent:** One place to see **what we’re building**, **why**, and **how we’ll build it in order** — without unnecessary complexity.

---

## 1. Executive summary (for VP / Senior PM)

| Question | Answer |
|----------|--------|
| **What** | An internal-style tool for **INDmoney** that turns **Google Play reviews** into a **weekly product pulse** (themes, quotes, summary, actions) plus a **standardized Exit Load fee explainer**, with outputs going to a **living Google Doc** and **email to subscribers**. |
| **Why** | Simulates how Product/Support use AI for **structured internal updates** and **standardized fee explanations**, per course brief. |
| **Who** | **Subscribers** sign up with email. **Admin** reviews a preview, then **appends to a master doc** and/or **sends email** — no silent automation for those actions. |
| **How (high level)** | Backend holds **review data** → **two real LLM API calls** (analysis, then final copy) → **preview** → admin triggers **MCP-style integrations** (Doc append + Gmail send). A **scheduler** only **refreshes reviews** into storage on a fixed interval — it does **not** auto-append or auto-send. |

**Non-goals:** 10M-user scale, microservices, heavy analytics UI, or replacing real APIs with editor-based LLMs.  
**Quality bar:** **Modular, testable, redeploy-friendly** — professional structure at learning-project scope.

---

## 2. Product surface (what users see)

| Screen | Purpose |
|--------|---------|
| **Home** | Two actions: **Subscribers Enter** → subscribe page; **Admin Enter** → admin console. |
| **Subscribers** | Email + Subscribe → stored for admin to select when sending. |
| **Admin** | **Status** (last time reviews were fetched / refreshed). **Create Preview** → fills **Preview** with latest structured content (email/doc JSON shape). **Sidebar:** subscriber emails with **checkboxes** (default: all selected). **Append to Doc** (MCP #1) and **Send Email** (MCP #2) work **independently** — admin may append without sending or send without appending; both use **current preview** content. |

**Approval gating (brief):** Nothing is written to the **Google Doc** and nothing is **sent via Gmail** until the admin **explicitly clicks** the corresponding action after reviewing the preview.

### 2.1 Global footer (every page)

All screens (**Home**, **Subscribers**, **Admin**) share a **footer** at the bottom of the page (same pattern as your prior project: metadata + attribution + collapsible architecture). Implementation: one reusable **layout/footer component** so content stays DRY.

| Element | Requirement |
|--------|----------------|
| **Last deployed** | Line such as: `Last Deployed On <date>, <time> <timezone>` — use **build/deploy time** (env injected at deploy or a single config constant updated on release); goal is honest “when this deployment snapshot is from.” |
| **Project title** | **Weekly Product Pulse and Fee Explainer** (exact wording from the course problem statement). |
| **Author** | `Project created by Aviral Rawat` |
| **LinkedIn** | Link: `https://www.linkedin.com/in/aviralrawat/` (opens in new tab; `rel="noopener noreferrer"`). |
| **Tooling** | `Built with Cursor` (plain text or small badge — keep minimal). |
| **System Design (Architecture)** | **Collapsible block** (accordion / `<details>`): header label **`System Design (Architecture)`**. **Default state: collapsed (closed)** — user expands to read. Current implementation loads full architecture text from **`apps/frontend/public/architecture-full.md`** (scrollable panel) so reviewers can inspect complete design context directly in-app. |

**UX notes:** Centered or full-width consistent with the rest of the UI; subtle border/green accent optional (match your reference). Footer must **not** block primary actions (subscribe, preview, append, send). Scroll: long accordion content should scroll inside the panel so the page doesn’t become unusable.

---

## 3. Key technical decisions

| Topic | Decision |
|-------|----------|
| **LLMs** | **Two explicit API calls** (not batched): **LLM1 (Groq)** — theme clustering, top themes, representative quotes (output **compact JSON**). **LLM2 (Gemini)** — leadership-style weekly note (**target ~120–150 words**, hard cap **≤250** per assignment), 3 one-line actions, formatting. **LLM2 input = LLM1 output only** (not full review dump). See **`SAMPLE_PULSE_OUTPUTS.md` §D** for token strategy. |
| **Scheduler** | **Every 48 hours:** fetch/update reviews into **`reviews_master.csv`** (and metadata for “last refreshed”). **Does not** append to Google Doc or send email. |
| **MCP #1** | **Append to Google Doc** with payload: `date`, `weekly_pulse`, `fee_scenario`, `explanation_bullets`, `source_links` — **newest block first** for CEO-style reading. |
| **MCP #2** | **Send email** via **Gmail** from the app (not “leave drafts in Gmail Drafts folder”). Subject includes **`Weekly Pulse + Fee Explainer —`**, **As on — &lt;date & time&gt;**, and **Weekly Pulse N** (serial). README explains this vs rubric wording “create draft.” |
| **Weekly Pulse serial `N`** | On each successful **Create Preview**, increment a persisted counter and assign **Weekly Pulse 1, 2, 3…** The **same N** labels the preview, the **Doc** block, and the **email** for that generation. Re-append / re-send **without** a new preview keeps the **same N** (demo-friendly). See **`SAMPLE_PULSE_OUTPUTS.md`** for mock Doc + email layout. |
| **Preview** | Single source of truth for what gets appended or sent; **no** extra guard that blocks repeat append/send for demos. |
| **PII** | No PII in generated artifacts; public review text only in controlled ways; subscriber emails only in send path. |
| **Resilience (light)** | Retries/backoff on LLM calls; **cache** fee explainer + scrape metadata; chunk/sample reviews to avoid context failures — **enough** for reliability, not enterprise LLM ops. |
| **Deploy** | **Frontend:** e.g. Vercel. **Backend:** e.g. Render / Fly.io / Railway — **host-agnostic** via env vars (see `.env.example`). |
| **Sources** | **Fund pages, Play Store URL, regulator links** are **author-provided** when implementing — not guessed or fabricated. |

### 3.1 Pulse logic & content rules (latest agreements)

| Topic | Rule |
|-------|------|
| **Themes** | Up to **5** themes; **top 3** by volume/frequency in the review window. |
| **Quotes** | **3** quotes — **one per top-3 theme**, verbatim (or minimal trim) from real reviews in that theme; **no** invented quotes. |
| **Weekly note & actions** | **LLM2**; assignment cap ≤**250** words — **target ~120–150** for exec readability + lower token use; **3** short **action lines**; **no PII**. |
| **Low review count** | If **0** reviews in window → block preview with clear message. If **too few** for 3 distinct quotes → **degraded mode** or **minimum threshold** (tunable); document in README — never fabricate reviews. |
| **Review quality gate** | Keep only meaningful reviews for analysis: minimum length + minimum word count, reject emoji-heavy/noisy content and vague alphanumeric junk; support English/Hindi text. |
| **Dedupe** | Use native Play Store **`reviewId`** as primary identity; skip already-seen IDs during fetch before normalization/merge. |
| **Fetch decision state** | Persist decision after each fetch: **`skip_no_new`**, **`skip_low_signal`**, **`run_ready`** (+ counters fetched/duplicate/filtered/meaningful) and expose via **`GET /api/reviews/decision`** for admin checks. |
| **Fee explainer** | **INDmoney — SBI Large Cap — Exit load** scenario; ≤6 bullets; 2 **official** links + **Last checked**; neutral; **links/text from author** at build time. |
| **Weekly Pulse N** | Increment on **Create Preview**; same **N** for Doc + email for that preview; see **`SAMPLE_PULSE_OUTPUTS.md`**. |

---

## 4. Data & integration map (conceptual)

```
Google Play (scraper) ──► reviews_master.csv ◄── 48h scheduler (fetch only)
                                 │
                                 ▼
                    Sample window (8–12 weeks) + quality filter
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
              LLM1 (Groq)               Fee explainer module
           themes / quotes              (Exit Load, links, cache)
                    │                         │
                    └────────────┬────────────┘
                                 ▼
              LLM2 (Gemini) — summary + actions + format
                                 │
                                 ▼
                         Preview payload (+ As on timestamp)
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
           MCP #1: Append Google Doc    MCP #2: Gmail send
           (admin click)               (admin click, selected emails)
```

---

## 5. Phase-by-phase implementation plan

Phases are **sequential**: finish + test each phase before the next.  
**Phase 0** is documentation-only; **Phase 1+** adds code in **thin vertical slices** so changes in one phase **rarely break** another (clear module boundaries).

---

### Phase 0 — Plan & documentation (no application code)

| | |
|--|--|
| **Goal** | Lock scope, deliverables, and phase names before coding. |
| **Deliverables** | **`SYSTEM_OVERVIEW.md`**, **`DEVELOPMENT_PLAN.md`**, **`Phase-0-Plan-Docs/`** (see **`Phase-0-Plan-Docs/README.md`**: `PHASES.md`, exit-criteria snapshot), **`PHASE-FOLDERS.md`** (naming rule), **`TODO.md`**, **`HEALTH.md`**, **`ASSIGNMENT_BRIEF.md`**, **`SAMPLE_PULSE_OUTPUTS.md`**, **`CHANGELOG.md`**, **`DEVLOG.md`**. **`.gitignore`**; **`apps/backend/`** + **`apps/frontend/`** placeholders + **`apps/README.md`** (no app code in Phase 0). |
| **Tests** | N/A (review only). |
| **Exit** | Stakeholder (you) sign-off that phases 1–N match expectations. |

---

### Phase 1 — Repository & runtime skeleton

| | |
|--|--|
| **Goal** | Runnable **backend** + **frontend** shells with **health checks** and **env template** — redeploy-friendly from day one. |
| **Code layout** | All app code under **`apps/`**: **`apps/backend/`** (API), **`apps/frontend/`** (web). Phase folders (`Phase-*`) stay documentation-only — see **`PHASE-FOLDERS.md`**. |
| **Backend** | Single service in **`apps/backend/`** (e.g. **Python + FastAPI**). `GET /api/health`. Folders e.g. `app/reviews`, `app/pulse`, `app/fee`, `app/integrations`, `app/subscribers`. `.env.example` (no secrets). |
| **Frontend** | Minimal app in **`apps/frontend/`** (e.g. **Next.js**). **Home** with **Subscribers Enter** + **Admin Enter** → routes `/subscribers` and `/admin` (placeholder pages). |
| **Tests** | Health endpoint test; smoke: home shows two buttons / links. |
| **Exit** | `npm`/`uv` run works locally; README stub updated. |

---

### Phase 2 — Reviews data layer & scheduled fetch

| | |
|--|--|
| **Goal** | **`reviews_master.csv`** as source of truth; **fetch + clean + append**; **48h job** only updates CSV + “last refreshed” metadata. |
| **Scope** | `google-play-scraper` (or equivalent); configurable filters (length, language, duplicates, etc.); **no LLM** in this phase. |
| **API** | Admin or internal: trigger fetch (for demo); scheduler calls same logic. |
| **Tests** | Cleaning rules on fixtures; CSV append idempotency; scheduler hook testable with mocked clock or manual trigger. |
| **Exit** | Admin **status** can show last refresh + review count from backend. |

---

### Phase 3 — Dual LLM pulse engine (Groq + Gemini)

| | |
|--|--|
| **Goal** | From sampled reviews: **LLM1** → structured analysis; **LLM2** → final pulse text + actions; **two HTTP calls**, retries on transient failures. |
| **Output** | LLM1 → **compact JSON** (`analysis`: ≤5 themes, **top 3**, **3 quotes**). LLM2 → note + **3** one-line actions; **LLM2 never receives full raw reviews** — only LLM1 JSON + instructions. |
| **Tests** | Mock API responses; validate schema; ensure **two** call sites in pipeline (not one batched request). |
| **Exit** | API or CLI can produce JSON for a **preview** without UI. |

---

### Phase 4 — Fee explainer (Exit Load)

| | |
|--|--|
| **Goal** | ≤6 bullets, 2 official links, **Last checked**, neutral tone; **cached** explainer; scrape updates **values/rules** when refreshed. |
| **Tests** | Mock HTML scrape; bullet/link count; cache read/write. |
| **Exit** | Fee block merges into preview payload. |

---

### Phase 5 — Preview package (doc + email shape)

| | |
|--|--|
| **Goal** | One **preview DTO** used by UI, Google Doc append, and email body: includes **As on — date & time**, **Weekly Pulse N**, full weekly + fee sections. |
| **Includes** | Doc append JSON fields per brief; email sections **Weekly pulse** / **Fee explanation**; subject line pattern + **N**; assign **N** on successful Create Preview. |
| **Tests** | Serialization tests; no PII helper tests. |
| **Exit** | `POST` “create preview” returns full payload for admin UI. |

---

### Phase 6 — MCP #1: Google Doc append

| | |
|--|--|
| **Goal** | **Append** new block (newest-first sections) to configured **Google Doc**; return **open URL** for new tab after success. |
| **Scope** | Real Google Docs API (or documented adapter); **no** auto-append from scheduler. |
| **Tests** | Integration test with test doc or mocked API; verify append payload shape matches brief. |
| **Exit** | Admin **Append to Doc** works end-to-end from preview. |

---

### Phase 7 — Subscribers store & MCP #2: Gmail send

| | |
|--|--|
| **Goal** | Persist subscribers; **send** to **selected** addresses using **Gmail** (SMTP or API); body/subject from preview; **not** leaving jobs in Drafts folder as final step. |
| **Tests** | Unit: recipient list filtering; integration: optional test account. |
| **Exit** | Admin **Send Email** delivers real mail per rubric format + timestamp in subject. |

---

### Phase 8 — Admin & subscriber UI (complete)

| | |
|--|--|
| **Goal** | Wire **Subscribers** page + **Admin** page: status, **Create Preview**, preview pane (structured JSON/email view), sidebar checkboxes (default all), **Append to Doc**, **Send Email**. **Include the global footer (§2.1) on every page:** metadata, LinkedIn, Built with Cursor, **System Design (Architecture)** accordion **closed by default**. |
| **Tests** | E2E smoke (Playwright/Cypress optional) or manual test script in README; spot-check footer on all routes. |
| **Exit** | Demo path: subscribe → admin preview → append and/or send; footer present and accordion works. |

---

### Phase 9 — Deploy, resilience polish, submission artifacts

| | |
|--|--|
| **Goal** | Deploy frontend + backend; document env vars; **README** for re-run, **where MCP actions fire**, fee scenario, **source list 4–6 URLs**; export **weekly note** / screenshots per `ASSIGNMENT_BRIEF.md`. |
| **Resilience** | Tune retries, logging, error messages for LLM/Gmail/Docs failures. |
| **Tests** | Full happy-path checklist; optional staging deploy smoke. |
| **Exit** | Prototype URL + README + checklist complete for deadline. |

---

## 6. How this reads to a senior reviewer

- **PM:** Clear user journey, brief alignment, phased delivery.  
- **Engineering:** Real external APIs (Groq, Gemini, Gmail, Google Docs, Play Store), modular boundaries, tests per phase, no fake “LLM in the editor.”  
- **Risk:** Scoped to **learning + bootcamp deliverables** — not hyperscale; structure is **intentionally evolvable** (swap DB, add queue later) without rewrites.

---

## 7. Document control

| Version | Change |
|---------|--------|
| 2025-03 | Replaced early phase plan with **Phase 0–9**, **VP summary**, **dual LLM**, **48h fetch-only scheduler**, **Subscribers/Admin Enter UI**, **MCP1 = Doc**, **MCP2 = Gmail send**, **independent actions**, **As on** timestamps. |
| 2025-03 | Added **§2.1 Global footer** (author, LinkedIn, Built with Cursor, title from brief, **System Design** accordion **default closed**); Phase 8 includes footer. |
| 2025-03 | Phase 0 clarified: **`DEVELOPMENT_PLAN.md`** = phase roadmap; **`TODO.md`** = granular tasks; added **`HEALTH.md`** template. |
| 2025-03 | Renamed **`DELIVERABLES_CHECKLIST.md`** → **`ASSIGNMENT_BRIEF.md`**; references updated across docs. |
| 2025-03 | **`SAMPLE_PULSE_OUTPUTS.md`**: mock Doc vs email; **Weekly Pulse N** serial + counter rules. |
| 2025-03 | **§3.1** pulse logic (quotes from top 3 themes, low-review handling, author-provided URLs); **`SYSTEM_OVERVIEW.md`** + **`CHANGELOG.md`**; all project `.md` synced pre-implementation. |
| 2025-03 | **`SAMPLE_PULSE_OUTPUTS.md`**: leadership-crisp layout + **§D LLM token strategy**; ARCHITECTURE LLM rows aligned (~120–150 word target, JSON-only to LLM2). |
| 2025-03 | **Phase 0 complete:** `.gitignore`, `apps/backend/` + `apps/frontend/` README placeholders, `DEVLOG.md`, **`Phase-0-Plan-Docs/`** (`PHASES.md`, exit criteria), `DEVELOPMENT_PLAN.md` Phase 0 ✅. |
| 2025-03 | **`Phase-0-Plan-Docs/`** + **`PHASE-FOLDERS.md`** naming convention. |
| 2025-03 | Removed redundant root **`PHASES.md`** (use **`Phase-0-Plan-Docs/PHASES.md`** only). |
| 2025-03 | Renamed **`backend/`** + **`frontend/`** → **`apps/backend/`** + **`apps/frontend/`** + **`apps/README.md`** (clearer vs `Phase-*` docs). |

*Update this section when phases complete or scope changes.*
