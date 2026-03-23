"""Gmail SMTP configuration."""

from __future__ import annotations

import os

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def get_gmail_smtp_user() -> str:
    """Full Gmail address used to authenticate (From)."""
    return os.getenv("GMAIL_SMTP_USER", "").strip()


def get_gmail_app_password() -> str:
    """App password (no spaces) from Google Account → App passwords."""
    return os.getenv("GMAIL_APP_PASSWORD", "").replace(" ", "").strip()


def gmail_send_configured() -> bool:
    return bool(get_gmail_smtp_user() and get_gmail_app_password())


def strict_recipients_only() -> bool:
    """If true, /gmail/send only allows addresses present in subscribers store."""
    return os.getenv("GMAIL_STRICT_RECIPIENTS", "true").strip().lower() in (
        "1",
        "true",
        "yes",
    )
