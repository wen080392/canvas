# apps/backend/app/services/crypto_service.py
"""CryptoService for encrypting and decrypting sensitive credentials.
Uses cryptography.fernet with an ENCRYPTION_KEY from environment.
If the key is missing, a temporary key is generated and a warning is logged.
"""
import os
import logging
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

class CryptoService:
    def __init__(self) -> None:
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            # Generate a temporary key and warn the user
            key = Fernet.generate_key()
            logger.warning(
                "ENCRYPTION_KEY not set – generated temporary key. "
                "Set ENCRYPTION_KEY in the environment for persistent encryption."
            )
        # Ensure the key is a valid base64-encoded 32‑byte value
        try:
            self._fernet = Fernet(key)
        except (ValueError, TypeError) as exc:
            raise ValueError("Invalid ENCRYPTION_KEY format") from exc

    def encrypt(self, plaintext: str) -> str:
        if plaintext is None:
            return None
        token = self._fernet.encrypt(plaintext.encode())
        return token.decode()

    def decrypt(self, token: str) -> str:
        if token is None:
            return None
        try:
            plaintext = self._fernet.decrypt(token.encode())
            return plaintext.decode()
        except InvalidToken as exc:
            logger.error("Failed to decrypt value – invalid token")
            raise exc
