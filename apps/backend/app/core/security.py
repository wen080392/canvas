"""
Cryptography service for encrypting sensitive data (AWS keys, GitHub tokens)
Uses Fernet symmetric encryption from the cryptography library
"""

import os
import logging
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


class CryptoService:
    """
    Service for encrypting and decrypting sensitive user credentials
    
    Uses Fernet (symmetric encryption) with a key from environment variables.
    If no key is configured, generates a temporary one with a warning.
    """
    
    def __init__(self):
        """Initialize the crypto service with encryption key"""
        self.encryption_key = os.getenv("ENCRYPTION_KEY")
        
        if not self.encryption_key:
            # Generate a temporary key and warn the admin
            self.encryption_key = Fernet.generate_key().decode()
            logger.warning(
                "⚠️  SECURITY WARNING: No ENCRYPTION_KEY found in environment variables!\n"
                "   A temporary key has been generated, but encrypted data will be lost on restart.\n"
                f"   Please add this to your .env file:\n"
                f"   ENCRYPTION_KEY={self.encryption_key}\n"
                "   For production, generate a new key with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            )
        
        # Initialize Fernet cipher
        try:
            self.cipher = Fernet(self.encryption_key.encode() if isinstance(self.encryption_key, str) else self.encryption_key)
        except Exception as e:
            logger.error(f"Failed to initialize Fernet cipher: {e}")
            raise ValueError("Invalid ENCRYPTION_KEY format. Generate a new one with Fernet.generate_key()")
    
    def encrypt(self, value: str) -> str:
        """
        Encrypt a plaintext string
        
        Args:
            value: The plaintext string to encrypt
            
        Returns:
            Encrypted string (base64 encoded)
            
        Example:
            >>> crypto = CryptoService()
            >>> encrypted = crypto.encrypt("AKIAIOSFODNN7EXAMPLE")
            >>> print(encrypted)
            'gAAAAABh...'
        """
        if not value:
            return ""
        
        try:
            encrypted_bytes = self.cipher.encrypt(value.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise ValueError(f"Failed to encrypt value: {e}")
    
    def decrypt(self, encrypted_value: str) -> Optional[str]:
        """
        Decrypt an encrypted string
        
        Args:
            encrypted_value: The encrypted string (base64 encoded)
            
        Returns:
            Decrypted plaintext string, or None if decryption fails
            
        Example:
            >>> crypto = CryptoService()
            >>> decrypted = crypto.decrypt("gAAAAABh...")
            >>> print(decrypted)
            'AKIAIOSFODNN7EXAMPLE'
        """
        if not encrypted_value:
            return None
        
        try:
            decrypted_bytes = self.cipher.decrypt(encrypted_value.encode())
            return decrypted_bytes.decode()
        except InvalidToken:
            logger.error("Failed to decrypt: Invalid token or wrong encryption key")
            return None
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
    
    def is_encrypted(self, value: str) -> bool:
        """
        Check if a value appears to be encrypted (Fernet format)
        
        Args:
            value: String to check
            
        Returns:
            True if the value looks like encrypted Fernet data
        """
        if not value:
            return False
        
        # Fernet tokens start with 'gAAAAA' after base64 encoding
        return value.startswith('gAAAAA')


# Global instance
_crypto_service: Optional[CryptoService] = None


def get_crypto_service() -> CryptoService:
    """
    Get or create the global CryptoService instance
    
    Returns:
        CryptoService instance
    """
    global _crypto_service
    
    if _crypto_service is None:
        _crypto_service = CryptoService()
    
    return _crypto_service
