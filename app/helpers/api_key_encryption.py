# app/helpers/api_key_encryption.py
from cryptography.fernet import Fernet
from passlib.context import CryptContext
import base64
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class APIKeyEncryption:
    def __init__(self):
        # Get encryption key from environment variable
        self.encryption_key = os.getenv("API_KEY_ENCRYPTION_KEY")
        if not self.encryption_key:
            # Generate a key (run this once and save to .env)
            self.encryption_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
            print(
                f" Generate and save this key to .env: API_KEY_ENCRYPTION_KEY={self.encryption_key}"
            )

        self.cipher = Fernet(self.encryption_key.encode())

    def encrypt_api_key(self, plain_key: str) -> str:
        """Encrypt API key for storage"""
        if not plain_key:
            return None

        # Log first/last 4 chars for debugging (safe)
        key_preview = (
            f"{plain_key[:4]}...{plain_key[-4:]}" if len(plain_key) > 8 else "***"
        )
        logger.debug(f"Encrypting API key: {key_preview}")

        encrypted = self.cipher.encrypt(plain_key.encode()).decode()
        logger.debug(f"Encryption successful, length: {len(encrypted)}")
        return encrypted

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key for use"""
        if not encrypted_key:
            logger.warning("Attempted to decrypt empty key")
            return None

        try:
            decrypted = self.cipher.decrypt(encrypted_key.encode()).decode()

            # Log first/last 4 chars for debugging (safe)
            key_preview = (
                f"{decrypted[:4]}...{decrypted[-4:]}" if len(decrypted) > 8 else "***"
            )
            logger.debug(f"Decrypted API key: {key_preview}")

            # Validate it looks like a real API key
            if not decrypted or len(decrypted) < 10:
                logger.error(
                    f"Decrypted key is suspiciously short: {len(decrypted)} chars"
                )

            return decrypted
        except Exception as e:
            logger.error(f"Failed to decrypt API key: {str(e)}")
            raise


api_key_encryption = APIKeyEncryption()
