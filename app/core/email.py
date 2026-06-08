# app/core/email.py
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
import os
from dotenv import load_dotenv
from app.core.logger import logger
import asyncio

# Load environment variables
load_dotenv()

# Brevo SMTP Configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "Rrolefit"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp-relay.brevo.com"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True").lower() == "true",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False").lower() == "true",
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


def send_verification_email(
    email_to: str, token: str, frontend_url: str = None
):  # Note: no async
    """Send email verification link to user (synchronous version for BackgroundTasks)"""
    if frontend_url is None:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

    verification_url = f"{frontend_url}/verify-email?token={token}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verify Your Email</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; padding: 20px 0;">
                <h2 style="color: #4F46E5;">Welcome to Rrolefit!</h2>
            </div>
            
            <div style="background: #f9f9f9; padding: 30px; border-radius: 10px;">
                <p style="font-size: 16px;">Hello!</p>
                <p style="font-size: 16px;">Thank you for registering. Please verify your email address by clicking the button below:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="background-color: #4F46E5; 
                              color: white; 
                              padding: 12px 30px; 
                              text-decoration: none; 
                              border-radius: 5px; 
                              display: inline-block;
                              font-weight: bold;">
                        Verify Email Address
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666;">Or copy and paste this link into your browser:</p>
                <p style="font-size: 14px; color: #4F46E5; word-break: break-all;">{verification_url}</p>
                
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                
                <p style="font-size: 12px; color: #999;">
                    This verification link will expire in 24 hours.<br>
                    If you didn't create an account with Rrolefit, you can safely ignore this email.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="Verify Your Email Address - Rrolefit",
        recipients=[email_to],
        body=html_content,
        subtype=MessageType.html,
    )

    try:
        fm = FastMail(conf)
        # Run the async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(fm.send_message(message))
        loop.close()
        logger.info(f"Verification email sent to {email_to}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {email_to}: {str(e)}")
        # Don't raise the exception - we don't want to fail registration if email fails
        return False
