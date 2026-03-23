# Deploy Automation (Minimal Manual Steps)

This repo now includes infrastructure/workflow automation so deployment is repeatable and less error-prone.

## What Is Automated

- `render.yaml` provisions backend service settings for Render (build/start/health/env defaults).
- `.github/workflows/reviews-fetch-cron.yml` triggers protected `/api/reviews/fetch` every 48h.
- `.github/workflows/deploy-smoke.yml` runs post-deploy checks for backend + frontend.

## One-Time Manual Steps (Cannot Be Fully Automated Here)

1. Connect your GitHub repo to Render.
2. Create the backend service from `render.yaml` (Render Blueprint).
3. Set sensitive env vars in Render (`sync: false` entries).
4. Connect your repo to Vercel and set frontend env vars.
5. Add GitHub repository secrets (see **`docs/GITHUB_ACTIONS_CRON_SETUP.md`** for step-by-step):
   - **`API_BASE_URL`** — Render backend base URL (no trailing slash), e.g. `https://indmoney-pulse-api.onrender.com`
   - **`CRON_TRIGGER_TOKEN`** — must match Render’s `CRON_TRIGGER_TOKEN` (and Vercel if you use the Next.js fetch proxy)
   - **`FRONTEND_URL`** — only for the optional `Deploy Smoke Check` workflow, not for the 48h fetch cron

## Runbooks

- Trigger fetch immediately: GitHub Actions -> `Reviews Fetch Cron` -> `Run workflow`
- Verify full deployment: GitHub Actions -> `Deploy Smoke Check` -> `Run workflow`

## Notes

- Keep `SCHEDULER_ENABLED=false` in hosted environments and rely on external cron.
- `STORAGE_MODE=ephemeral` is the default; set `persistent` if your host guarantees durable disk (Render Starter still uses ephemeral disk unless you add a persistent disk).
- **Gmail:** outbound SMTP (`smtp.gmail.com:587` + app password) works on **Render Starter**; it is blocked on Render **Free** web services.
