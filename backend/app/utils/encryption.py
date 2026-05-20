"""Fernet-based symmetric encryption for storing sensitive credentials."""

from cryptography.fernet import Fernet

from app.config import settings


def _get_fernet() -> Fernet:
    """Return a Fernet instance using the configured encryption key."""
    return Fernet(settings.CREDENTIAL_ENCRYPTION_KEY.encode())


def encrypt(plaintext: str) -> str:
    """Encrypt a plaintext string using Fernet symmetric encryption.

    Args:
        plaintext: The string to encrypt.

    Returns:
        The base64-encoded ciphertext string.
    """
    f = _get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """Decrypt a Fernet-encrypted ciphertext string.

    Args:
        ciphertext: The base64-encoded ciphertext to decrypt.

    Returns:
        The decrypted plaintext string.
    """
    f = _get_fernet()
    return f.decrypt(ciphertext.encode()).decode()


def generate_key() -> str:
    """Generate a new Fernet encryption key.

    Returns:
        A URL-safe base64-encoded 32-byte key as a string.
    """
    return Fernet.generate_key().decode()
