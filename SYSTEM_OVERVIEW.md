# System Overview — Weekly Product Pulse & Fee Explainer

**One-liner:** Turn **INDmoney** Google Play reviews into a **weekly pulse** (themes, quotes, summary, actions) plus an **Exit Load fee explainer**, then let an **admin** append to a **master Google Doc** and/or **email subscribers** — after **Create Preview**, with **no** auto-append or auto-send from background jobs.

**Course alignment:** See **`ASSIGNMENT_BRIEF.md`**. **Design detail & phases:** **`ARCHITECTURE.md`**.

---

## Who does what

| Actor | Action |
|-------|--------|
| **Subscriber** | Enters email on **Subscribers Enter** → stored for admin. |
| **Admin** | **Admin Enter** → sees fetch status, **Create Preview** (LLM1 + LLM2), **Append to Doc** / **Send Email** independently; selects recipients for email. |
| **Scheduler (48h)** | Refreshes **`reviews_master.csv`** only (native Play Store `reviewId` dedupe + meaningful filter), stores decision metadata (`skip_no_new` / `skip_low_signal` / `run_ready`), and does not append to Doc or send mail. |

---

## Intelligence stack

| Step | Model | Role |
|------|--------|------|
| **LLM1** | Groq | **Internal analysis:** ≤5 themes, **top 3 themes**, **3 quotes** (1 per top theme, verbatim from reviews). |
| **LLM2** | Gemini | **Final communication:** weekly note **≤250 words** (**~120–150 target** for exec skim), **3** short actions; input = **LLM1 JSON only** (saves tokens). |

Two **explicit** API calls; not batched into one HTTP round-trip.

---

## Outputs

| Output | Channel |
|--------|---------|
| **Weekly Pulse N** | Serial number increments on **Create Preview**; same **N** on Doc block and email for that preview. |
| **Doc** | Append-only Google Doc, **newest first**; includes **As on — date & time** (default **Asia/Kolkata**). |
| **Email** | Gmail send from app; subject includes **`Weekly Pulse + Fee Explainer —`**, **As on**, **Weekly Pulse N**. |

**Mock layouts:** **`SAMPLE_PULSE_OUTPUTS.md`**.

---

## Integrations & honesty

- **URLs & official fee text:** Provided by you — we do **not** invent INDmoney/fund URLs or regulatory links.
- **Secrets:** Environment variables only; see **`.env.example`** when implemented.
- **MCP:** **#1** append Doc; **#2** send email (approved send, not Gmail Drafts folder as final step — documented in README).

---

## Related files

| File | Purpose |
|------|---------|
| `ARCHITECTURE.md` | Phases 0–9, footer spec, technical decisions |
| `ASSIGNMENT_BRIEF.md` | Rubric checklist + submission artifacts |
| `DEVELOPMENT_PLAN.md` | Phase checkboxes (Phase 0 ✅) |
| `Phase-0-Plan-Docs/` | Phase 0 — plan & docs artifacts |
| `apps/` | API + web app code (`apps/backend`, `apps/frontend`) |
| `PHASE-FOLDERS.md` | Phase folder naming + `apps/` vs `Phase-*` |
| `DEVLOG.md` | Session notes |
| `SAMPLE_PULSE_OUTPUTS.md` | Mock Doc + email |
| `HEALTH.md` | Last-run health |
| `Brain.md` | General PM/build philosophy |
