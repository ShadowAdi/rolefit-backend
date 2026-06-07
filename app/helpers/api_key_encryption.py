# app/helpers/api_key_encryption.py
from cryptography.fernet import Fernet
import base64
import os
import logging

logger = logging.getLogger(__name__)


class APIKeyEncryption:
    def __init__(self):
        self.encryption_key = os.getenv("API_KEY_ENCRYPTION_KEY")
        if not self.encryption_key:
            # In production, this should raise an error
            raise ValueError(
                "API_KEY_ENCRYPTION_KEY environment variable is required. "
                "Please set a fixed key in your .env file and restart."
            )

        # Ensure the key is properly formatted
        try:
            self.cipher = Fernet(self.encryption_key.encode())
            logger.info("API key encryption initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise

    def encrypt_api_key(self, plain_key: str) -> str:
        if not plain_key:
            return None
        try:
            encrypted = self.cipher.encrypt(plain_key.encode()).decode()
            return encrypted
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt_api_key(self, encrypted_key: str) -> str:
        if not encrypted_key:
            return None
        try:
            decrypted = self.cipher.decrypt(encrypted_key.encode()).decode()
            return decrypted
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise


api_key_encryption = APIKeyEncryption()
