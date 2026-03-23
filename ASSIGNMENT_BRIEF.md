# Assignment Brief — Weekly Product Pulse & Fee Explainer

**Purpose:** Track **must-haves from the course assignment** vs **extra scope** we add.  
**Rule:** We never ship without satisfying the brief; extra features are optional polish.

**Due:** Mar 25, 11:59 PM (Asia/Kolkata)

---

## A. Official brief — must build (functional)

### Part A — Weekly review pulse

| # | Requirement | Status | Notes |
|---|-------------|--------|--------|
| A1 | Input: **public reviews CSV** covering **last 8–12 weeks** | [x] | `reviews_master.csv` + scheduler/manual fetch in place. |
| A2 | Group reviews into **max 5 themes** | [x] | LLM1 clustering + structured analysis pipeline implemented. |
| A3 | Identify **top 3 themes** | [x] | Returned in `analysis.top_3_theme_names`. |
| A4 | Extract **3 real user quotes** | [x] | **1 quote per top-3 theme** (verbatim from supplied reviews); see `ARCHITECTURE.md` §3.1. |
| A5 | Generate **≤250-word** weekly note | [x] | LLM2; **target ~120–150 words** for leadership scan (still within cap). |
| A6 | Add **3 action ideas** | [x] | LLM2 output (three action lines). |
| A7 | **No PII** in outputs | [x] | Output shape/prompting keeps public-review-only content; no subscriber PII in pulse artifacts. |

### Part B — Fee explainer (single scenario)

| # | Requirement | Status | Notes |
|---|-------------|--------|--------|
| B1 | **One** fee scenario (e.g. Exit Load) | [x] | Exit Load scenario implemented and documented. |
| B2 | **≤6 bullet** structured explanation | [x] | Fee explainer returns bounded bullet list format. |
| B3 | **2 official source links** | [x] | Source link list included in fee block. |
| B4 | **“Last checked:”** line | [x] | `last_checked_iso` included in fee payload. |
| B5 | **Neutral, facts-only** — no recommendations or comparisons | [x] | Neutral explainer wording flow implemented. |
| B6 | Tone guardrails in prompt + review | [x] | Guardrails reflected in pipeline/formatting constraints. |

### MCP actions — approval-gated

| # | Requirement | Status | Notes |
|---|-------------|--------|--------|
| M1 | **Append to Notes/Doc** with payload shape: `date`, `weekly_pulse`, `fee_scenario`, `explanation_bullets`, `source_links` | [x] | Implemented via Google Doc append endpoint; approval-gated from Admin. |
| M2 | **Email content + send** — Subject pattern: `Weekly Pulse + Fee Explainer —` + **As on** + **Weekly Pulse N** | [x] | Implemented via Gmail endpoint; admin-triggered send from preview. |
| M3 | Body sections: **Weekly pulse** + **Fee explanation** | [x] | Structured in HTML + plain preview/send payload. |
| M4 | **All** MCP actions **approval-gated** (no silent writes) | [x] | **Append to Doc** / **Send Email** only after admin review of **Create Preview**. |
| M5 | Brief **“No auto-send”** | [x] | **Locked:** No SMTP without admin **Send**; scheduler **never** sends mail or appends Doc — only refreshes reviews CSV. |

### Skills alignment (brief)

| Skill | Covered by |
|-------|------------|
| LLM structuring | LLM2 final comms |
| Theme clustering | LLM1 |
| Quote extraction | LLM1 |
| Controlled summarization | LLM2 + limits |
| Workflow sequencing | Ingest → LLM1 → LLM2 → Create Preview → Append Doc / Send email |
| MCP tool calling | Append Doc + send email (materialized content = draft equivalent) |
| Approval gating | Dashboard before MCP side effects |

---

## B. Course submission artifacts

| # | Deliverable | Status |
|---|-------------|--------|
| D1 | **Working prototype link** *or* **≤3 min demo video** | ☐ |
| D2 | **Weekly note** (MD / PDF / Doc) | ☐ |
| D3 | **Notes/Doc snippet** showing appended entry | ☐ |
| D4 | **Email** screenshot or pasted text (sent mail or preview — README notes which) | ☐ |
| D5 | **Reviews CSV sample** | ☐ |
| D6 | **Source list** (4–6 URLs) | ☐ |
| D7 | **README:** how to re-run, **where MCP approval happens**, **fee scenario** covered | ☐ |

---

## C. Our extended scope (optional — does not replace brief)

| Item | Status |
|------|--------|
| Google Play fetch via `google-play-scraper` → master CSV | [x] |
| Two LLMs: **LLM1** internal analysis, **LLM2** final comms (documented) | [x] |
| Gmail real sends to subscribers | [x] |
| Admin UI: **Subscribers Enter** + **Admin Enter** (no separate Automation tab) | [x] |
| Scheduler **48h**: **fetch reviews → CSV only** (no auto-append, no auto-send) | [x] |
| **Weekly Pulse N** serial + **As on** timestamp in Doc & email | [x] |
| **Deploy:** e.g. Vercel + Render/Fly (or similar) | ☐ |

---

## D. Resolved alignment (document in README when implemented)

1. **“No auto-send”** — **Resolved:** Nothing is emailed unless admin clicks **Send Email**; background job only updates `reviews_master.csv`.
2. **CSV** — `reviews_master.csv` is the master store; Play Store fetch populates it; grader can also use a static CSV sample.

## E. Sources & URLs (author-provided)

**Fee explainer official links and INDmoney/fund page URLs are supplied by the project author** — not invented during implementation. List **4–6 URLs** in README for submission.

---

*Update statuses as phases complete.*
