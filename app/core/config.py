# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Brevo SMTP Configuration
    MAIL_USERNAME: str
    MAIL_PASSWORD: str  # Your SMTP key, not account password!
    MAIL_FROM: str
    MAIL_FROM_NAME: str = "Rolefit"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp-relay.sendinblue.com"
    MAIL_STARTTLS: bool = True  # For port 587
    MAIL_SSL_TLS: bool = False

    # Frontend URL for verification links
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
