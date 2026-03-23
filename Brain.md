# PROJECT_BRAIN.md

## Purpose

This file provides lightweight guidance for building AI projects with the Cursor coding assistant.

The developer is a Product Manager learning the technical side of AI systems such as:

* Retrieval Augmented Generation (RAG)
* LLM applications
* agents and voice systems
* evaluation pipelines

The goal is to **learn system design by building working systems**, not by over-optimizing architecture or documentation.

---

## Development Philosophy

Projects should prioritize:

* building working systems quickly
* understanding how components interact
* learning engineering trade-offs

Avoid unnecessary complexity.

For learning purposes, “production-style thinking” means:

* modular code structure
* separation of concerns
* clear system components
* basic logging and error handling

It does **not** mean:

* microservices
* distributed infrastructure
* heavy abstraction layers

---

## Working Style

Development should follow this simple loop:

1. Define the goal of the session
2. Implement the feature or component
3. Test and observe system behavior
4. Reflect on what was learned

When in doubt, **ship working code first. Document and reflect after.**

---

## Project Structure

Each project typically maintains these files:

README.md – project overview and setup instructions

SYSTEM_OVERVIEW.md – short executive summary of this product

ARCHITECTURE.md – system design, phases, pulse logic (§3.1)

ASSIGNMENT_BRIEF.md – course brief requirements + submission checklist

SAMPLE_PULSE_OUTPUTS.md – mock Google Doc block + email (Weekly Pulse N)

DEVELOPMENT_PLAN.md – phase-by-phase roadmap

Phase-0-Plan-Docs/ – Phase 0 artifacts (Plan & Docs)

apps/ – runnable API + web (`apps/backend/`, `apps/frontend/`); not the same as Phase-* folders

PHASE-FOLDERS.md – phase folder naming (`Phase-<n>-<ShortTitle>`)

TODO.md – granular session tasks

DEVLOG.md – session notes

HEALTH.md – last-run status of pipelines / integrations

CHANGELOG.md – milestones and notable doc/code changes

---

## Documentation Rules

Documentation should **not interrupt coding flow**.

Update documentation only:

* at the end of a development session
* after completing a major feature
* when a significant architectural decision is made

---

## Engineering Practices

Follow basic engineering habits:

* never hardcode API keys
* use environment variables for secrets
* keep dependencies explicit
* write modular and readable code
* test important deterministic logic when possible

---

## Expected Outcome

By the end of a project, the developer should understand:

* how the system works
* why each component exists
* what trade-offs were made

The goal is **practical understanding through building**.

---

## This project (Milestone 2 — Weekly Product Pulse & Fee Explainer)

Keep the same philosophy: **modular, working code**, env-based secrets, **no invented URLs** for INDmoney / funds / regulators — **you provide** official links and page targets when we implement fee explainer and Play Store scope.

**Where to look:**

| Doc | What |
|-----|------|
| `SYSTEM_OVERVIEW.md` | Short product + stack summary |
| `ARCHITECTURE.md` | Full design, phases, footer UI, pulse logic |
| `ASSIGNMENT_BRIEF.md` | Rubric + submission checklist |
| `SAMPLE_PULSE_OUTPUTS.md` | Mock Doc block + email (Weekly Pulse N) |
| `DEVELOPMENT_PLAN.md` | Phase 0–9 progress (Phase 0 ✅) |
| `apps/` | Runnable **backend** + **frontend** (not inside `Phase-*`) |
| `Phase-0-Plan-Docs/` | Phase 0 artifacts (Plan & Docs) |
| `PHASE-FOLDERS.md` | Phase folder naming: `Phase-<n>-<ShortTitle>` |
| `DEVLOG.md` | Session notes |
| `CHANGELOG.md` | Milestones / doc sync |

**Frontend theme:** When we reach the UI phase, we’ll **ask you for theme preferences** and suggest options.

**Implementation:** Cursor will **guide** you on secrets, Gmail, Google Docs API, and MCP wiring — step by step.
