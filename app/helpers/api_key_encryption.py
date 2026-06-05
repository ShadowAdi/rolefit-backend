from cryptography.fernet import Fernet
from passlib.context import CryptContext
import base64
import os
from typing import Optional


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
        return self.cipher.encrypt(plain_key.encode()).decode()

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key for use"""
        if not encrypted_key:
            return None
        return self.cipher.decrypt(encrypted_key.encode()).decode()


api_key_encryption = APIKeyEncryption()
