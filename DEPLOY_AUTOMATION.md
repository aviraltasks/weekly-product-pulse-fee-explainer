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
5. Add GitHub repository secrets:
   - `API_BASE_URL`
   - `FRONTEND_URL`
   - `CRON_TRIGGER_TOKEN`

## Runbooks

- Trigger fetch immediately: GitHub Actions -> `Reviews Fetch Cron` -> `Run workflow`
- Verify full deployment: GitHub Actions -> `Deploy Smoke Check` -> `Run workflow`

## Notes

- Keep `SCHEDULER_ENABLED=false` in hosted environments and rely on external cron.
- Keep `STORAGE_MODE=ephemeral` on free-tier hosts unless you migrate to persistent storage.
