"""Pytest defaults: no background scheduler; tests may override REVIEWS_DATA_DIR."""

from __future__ import annotations

import os

# Must run before `app.main` import. Disables load_dotenv(override=True) so .env cannot flip SCHEDULER etc.
os.environ["DOTENV_NO_OVERRIDE"] = "1"
# Must run before `app.main` import so lifespan does not start APScheduler.
os.environ.setdefault("SCHEDULER_ENABLED", "false")
