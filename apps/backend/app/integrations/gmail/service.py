"""
Send mail via standard Gmail SMTP: smtp.gmail.com:587, STARTTLS, then AUTH + SEND.
Requires GMAIL_SMTP_USER and GMAIL_APP_PASSWORD (Google App Password).
Outbound SMTP is allowed on Render Starter; it is blocked on Render Free web services.
"""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.integrations.gmail.config import (
    SMTP_HOST,
    SMTP_PORT,
    get_gmail_app_password,
    get_gmail_smtp_user,
)

logger = logging.getLogger(__name__)


def send_email(
    *,
    to_emails: list[str],
    subject: str,
    body_plain: str,
    body_html: str | None = None,
    from_email: str | None = None,
    app_password: str | None = None,
) -> None:
    """
    Deliver mail (not Drafts). Uses STARTTLS on port 587.
    If body_html is set, sends multipart/alternative (plain + HTML).
    """
    user = from_email or get_gmail_smtp_user()
    pwd = app_password or get_gmail_app_password()
    if not user or not pwd:
        raise ValueError("Gmail SMTP user and app password must be set")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = ", ".join(to_emails)
    msg.set_content(body_plain, subtype="plain", charset="utf-8")
    if body_html:
        msg.add_alternative(body_html, subtype="html", charset="utf-8")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=60) as smtp:
        smtp.starttls()
        smtp.login(user, pwd)
        smtp.send_message(msg)

    logger.info("Gmail SMTP sent to %s recipient(s)", len(to_emails))


def send_plain_email(
    *,
    to_emails: list[str],
    subject: str,
    body_plain: str,
    from_email: str | None = None,
    app_password: str | None = None,
) -> None:
    """Backward-compatible: plain text only."""
    send_email(
        to_emails=to_emails,
        subject=subject,
        body_plain=body_plain,
        body_html=None,
        from_email=from_email,
        app_password=app_password,
    )
