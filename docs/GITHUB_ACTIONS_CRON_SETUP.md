# GitHub Actions — 48h review fetch (one-time setup)

The workflow **Reviews Fetch Cron** (`.github/workflows/reviews-fetch-cron.yml`) calls your Render backend:

`POST /api/reviews/fetch` with header `X-Cron-Token: <secret>`

It runs on a **schedule** (≈ every 2 days, UTC) and can be run **manually** anytime.

---

## 1. Enable Actions (if needed)

1. Open your repo on GitHub: `https://github.com/<you>/weekly-product-pulse-fee-explainer`
2. **Settings** → **Actions** → **General**
3. Under **Actions permissions**, choose **Allow all actions and reusable workflows** (or your org’s equivalent).
4. Save.

---

## 2. Add repository secrets (required)

**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret name | Value | Notes |
|-------------|--------|--------|
| `API_BASE_URL` | `https://indmoney-pulse-api.onrender.com` | Your Render **HTTPS** base URL, **no** trailing slash. |
| `CRON_TRIGGER_TOKEN` | *(same string as Render)* | Must **exactly** match Render env var `CRON_TRIGGER_TOKEN`. |

**Important**

- Generate a long random token once (e.g. 32+ characters), store it in:
  - **Render** → your web service → **Environment** → `CRON_TRIGGER_TOKEN`
  - **GitHub** → same name `CRON_TRIGGER_TOKEN`
- If Vercel proxies the admin “Refresh reviews” button, also set the same token in Vercel as `CRON_TRIGGER_TOKEN`.

`FRONTEND_URL` is **not** used by this workflow (only by `deploy-smoke.yml`).

---

## 3. Verify the workflow file is on `main`

The file must exist on the default branch:

- `.github/workflows/reviews-fetch-cron.yml`

After you push, GitHub picks it up automatically.

---

## 4. Test without waiting for the schedule

1. **Actions** tab → **Reviews Fetch Cron**
2. **Run workflow** → branch `main` → **Run workflow**
3. Open the run → confirm steps **Health check** and **Trigger protected fetch** are green.

If **Validate required secrets** fails, the two secrets are missing or empty.

If **Trigger protected fetch** returns `401`, the token on GitHub does not match Render.

If **Trigger protected fetch** returns `503`, `CRON_TRIGGER_TOKEN` is not set on Render.

---

## 5. Schedule (UTC)

The cron expression is in the workflow file. Default intent: **about every 48 hours** using “every 2nd day of the month” in UTC (GitHub does not support a true rolling 48h interval in `schedule`).

To change the time, edit the `cron:` line in `reviews-fetch-cron.yml` and push.

---

## 6. CLI alternative (optional)

If you use [GitHub CLI](https://cli.github.com/) (`gh`) and are logged in:

```bash
cd /path/to/repo
gh secret set API_BASE_URL --body "https://indmoney-pulse-api.onrender.com"
gh secret set CRON_TRIGGER_TOKEN --body "YOUR_LONG_SECRET_MATCHING_RENDER"
```

Do **not** commit the token to the repo.

---

## Summary checklist

- [ ] `API_BASE_URL` secret set (Render base URL)
- [ ] `CRON_TRIGGER_TOKEN` secret set and matches Render (and Vercel if you use the proxy)
- [ ] Manual **Run workflow** succeeds
- [ ] Optional: watch **Actions** after the next scheduled run
