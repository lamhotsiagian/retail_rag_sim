from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_gmail_smtp(to_email: str, subject: str, body: str) -> str:
    host = os.getenv("GMAIL_SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("GMAIL_SMTP_PORT", "587"))
    user = os.getenv("GMAIL_SMTP_USER", "")
    app_password = os.getenv("GMAIL_SMTP_APP_PASSWORD", "")

    if not user or not app_password:
        raise ValueError("Missing GMAIL_SMTP_USER or GMAIL_SMTP_APP_PASSWORD in .env")

    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(user, app_password)
        smtp.send_message(msg)

    return "sent"
