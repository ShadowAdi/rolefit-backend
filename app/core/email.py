# app/core/email.py
import requests
import os
from dotenv import load_dotenv
from app.core.logger import logger

load_dotenv()


def send_verification_email(email_to: str, token: str, frontend_url: str = None):
    if frontend_url is None:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

    verification_url = f"{frontend_url}/verify-email?token={token}"

    api_key = os.getenv("BREVO_API_KEY")
    mail_from = os.getenv("MAIL_FROM")
    mail_from_name = os.getenv("MAIL_FROM_NAME", "Rolefit")

    if not api_key:
        logger.error("BREVO_API_KEY not found in environment")
        return False

    if not mail_from:
        logger.error("MAIL_FROM not found in environment")
        return False

    headers = {
        "accept": "application/json",
        "api-key": api_key,  # Must be a REST API key, not SMTP key
        "content-type": "application/json",
    }

    data = {
        "sender": {
            "name": mail_from_name,
            "email": mail_from,  # Must be a verified sender in Brevo
        },
        "to": [{"email": email_to}],
        "subject": "Verify Your Email Address - Rolefit",
        "htmlContent": f"""...""",  # keep your existing HTML
    }

    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=data,
            headers=headers,
            timeout=30,
        )
        if response.status_code == 201:
            logger.info(f"Verification email sent to {email_to}")
            return True
        else:
            logger.error(f"Brevo error {response.status_code}: {response.text}")
            return False
    except requests.exceptions.Timeout:
        logger.error(f"Timeout sending email to {email_to}")
        return False
    except Exception as e:
        logger.error(f"Error sending email to {email_to}: {str(e)}")
        return False
