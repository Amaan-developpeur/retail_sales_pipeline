import logging
import smtplib
from email.mime.text import MIMEText
import requests

# --- Configuration ---
ALERT_MODE = "slack"  # choose "slack" or "email"

from dotenv import load_dotenv
import os
import requests
import logging

load_dotenv()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
EMAIL_CONFIG = {
    "from": "alertbot@example.com",
    "to": "your_email@example.com",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "your_email@example.com",
    "smtp_pass": "YOUR_APP_PASSWORD"  # use an App Password, not your actual one
}

def send_alert(subject: str, message: str):
    try:
        if ALERT_MODE == "slack":
            payload = {"text": f":rotating_light: *{subject}*\n{message}"}
            resp = requests.post(SLACK_WEBHOOK_URL, json=payload)
            if resp.status_code != 200:
                raise Exception(f"Slack webhook failed: {resp.text}")
            logging.info("Slack alert sent successfully.")

        elif ALERT_MODE == "email":
            msg = MIMEText(message)
            msg["Subject"] = subject
            msg["From"] = EMAIL_CONFIG["from"]
            msg["To"] = EMAIL_CONFIG["to"]

            with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
                server.starttls()
                server.login(EMAIL_CONFIG["smtp_user"], EMAIL_CONFIG["smtp_pass"])
                server.send_message(msg)
            logging.info("Email alert sent successfully.")

    except Exception as e:
        logging.error(f"Alert delivery failed: {e}")
