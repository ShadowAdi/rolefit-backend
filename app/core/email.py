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
        "htmlContent": f"""
        <!DOCTYPE html>
        <html>
          <body style="margin:0;padding:0;background-color:#f4f4f7;font-family:Arial,Helvetica,sans-serif;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f7;padding:32px 0;">
              <tr>
                <td align="center">
                  <table role="presentation" width="480" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:8px;padding:40px;">
                    <tr>
                      <td style="text-align:center;">
                        <h1 style="margin:0 0 16px;font-size:22px;color:#111827;">Verify your email</h1>
                        <p style="margin:0 0 24px;font-size:15px;line-height:1.5;color:#4b5563;">
                          Thanks for signing up for {mail_from_name}. Please confirm your email address to activate your account.
                        </p>
                        <a href="{verification_url}"
                           style="display:inline-block;background-color:#a3e635;color:#030712;text-decoration:none;font-size:15px;font-weight:bold;padding:12px 28px;border-radius:6px;">
                          Verify Email Address
                        </a>
                        <p style="margin:24px 0 0;font-size:13px;color:#6b7280;">
                          Or paste this link into your browser:<br>
                          <a href="{verification_url}" style="color:#65a30d;word-break:break-all;">{verification_url}</a>
                        </p>
                        <p style="margin:24px 0 0;font-size:12px;color:#9ca3af;">
                          If you didn't create an account, you can safely ignore this email.
                        </p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """,
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
