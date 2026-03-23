# Sample outputs — Doc append vs email (mock)

**Purpose:** Show **crisp** layouts for **Doc** and **email** — readable in **under ~2 minutes** for busy leadership.  
**Assignment still satisfied:** Themes, top 3, 3 quotes, weekly note **≤250 words** (we **target ~120–150 words** for the note to stay scannable and save tokens), 3 actions, fee bullets ≤6.

**Numbers / links:** Illustrative. **Fee URLs** = author-provided at build time.

**Synced:** Quotes = 1 per top-3 theme · **Weekly Pulse N** on Create Preview · **As on** timestamp · **§D** = token strategy.

---

## D. LLM token strategy (optimal use of free / low tiers)

| Layer | What we do |
|-------|----------------|
| **Before LLM** | Cap input: sample **N reviews** (e.g. 120–200) + **truncate** each review (e.g. 300–400 chars) for the model; drop duplicates / low-signal rows in code (no tokens). |
| **LLM1 (Groq)** | In: **compressed batch** only. Out: **strict JSON** (themes, top 3, 3 short quotes) — **no** prose essay. **Do not** pass full reviews again to LLM2. |
| **LLM2 (Gemini)** | In: **only** LLM1 JSON + 10–15 lines of instructions + **target word count** (~120–150 for leadership; hard cap ≤250). **No** raw review dump. |
| **Fee explainer** | **Cached** text + scrape refresh; **no** extra LLM call when cache hit. |
| **Retries** | Only on failure; **no** retry loops that multiply spend. |

This keeps **two small calls** per preview instead of stuffing the whole CSV into every prompt.

---

## A. Block appended to Google Doc (newest on top)

**Leadership-first layout** — dense, skimmable.

```
════════════════════════════════════════════════════════════
Weekly Pulse 3 · As on — 17 Mar 2025, 18:45 IST
════════════════════════════════════════════════════════════

PULSE (TL;DR)
Mixed sentiment. Top noise: app load during peaks; KYC copy clarity; in‑app support
visibility. Smaller volume: fund discovery, notifications.

TOP 3 THEMES (by volume)
1) App performance & stability
2) Account / KYC / onboarding
3) Customer support

EVIDENCE (1 quote / theme — verbatim, PII stripped)
• Performance: "…portfolio view sometimes takes a few seconds when markets move fast."
• KYC: "…one screen had unclear instructions for address proof."
• Support: "…wish there was clearer ticket status inside the app."

NOTE (~120–150 words; assignment cap ≤250)
Users still flag latency on portfolio/holdings during volatile windows. KYC completes
quickly for many, but document requirements confuse a subset of new users. Support
reviews focus on response time and visibility—not tone—suggesting a product gap on
status inside the app. Discovery/education and notifications are lower volume but
repeat for newer investors. Overall: mixed-to-positive; prioritize load performance,
onboarding verification copy, and in-app ticket transparency. No PII in this summary.

ACTIONS (3 — one line each)
1) QA: stress-test portfolio load under peak traffic; track by build.
2) PM: ship a single checklist screen for required verification documents.
3) PM: spec visible ticket state for in-app support requests.

────────────────────────────────────────────────────────────
FEE — INDmoney · SBI Large Cap · Exit load
────────────────────────────────────────────────────────────
• [Short rule 1 — your source]
• [Short rule 2 — your source]
• [Short rule 3 — your source]
• [Short rule 4 — optional; max 6 bullets total]

Sources: [URL 1] · [URL 2]   |   Last checked: 17 Mar 2025

(JSON MCP payload: date, weekly_pulse, fee_scenario, explanation_bullets, source_links)
```

**Optional appendix (same append, if you want full rubric detail):** one line *“All 5 clustered themes available in API/export.”* — keeps the **doc** short; **full** theme list can live in JSON only.

---

## B. Email (same content, tighter)

**Subject**

```
Weekly Pulse + Fee Explainer — As on 17 Mar 2025, 18:45 IST — Weekly Pulse 3
```

**Body (plain + HTML)** — section labels are scannable and self-explanatory; HTML adds a centered title line, spacing, and `<hr>` before the fee block.

```
WEEKLY PRODUCT PULSE: 17 Mar 2025, 18:45 IST

[INDMONEY intro + data basis]

TOP 3 CUSTOMER THEMES (by volume among sampled reviews): …

CUSTOMER VERBATIM QUOTES (Play Store excerpts; one per top theme): …

EXECUTIVE ANALYSIS (AI-assisted summary — not legal, tax, or investment advice): …

PRIORITY ACTIONS (suggested next steps): …

────────────────────────────────[rule]────────────────────────────────

KNOWLEDGE BASE: FEE EXPLAINER — EXIT LOAD (reference only): …

As on — …
— Not investment advice. Review themes may not reflect all users.
```

---

## C. Counter rule

| Event | Behavior |
|-------|----------|
| **Create Preview** | Next **Weekly Pulse N**; preview shows **N**. |
| **Append / Send** | Same **N** as current preview. |
| **New preview** | **N ← N+1**; re-append without new preview keeps **N**. |

---

*Mocks only. Replace fee placeholders with your official sources.*
