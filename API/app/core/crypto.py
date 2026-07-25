"""
Anchor — Field-Level Encryption Helper.

App-level encryption for sensitive free-text fields (notes, transcripts, phone numbers)
before storing ciphertext at rest in AWS RDS Postgres.
Uses Fernet symmetric encryption (AES-128-CBC + HMAC-SHA256).
"""

from __future__ import annotations

import base64
import hashlib
from cryptography.fernet import Fernet

from app.core.config import settings


def _get_fernet() -> Fernet:
    """Initialize Fernet instance using FIELD_ENCRYPTION_KEY or dev fallback key."""
    key = settings.field_encryption_key
    try:
        # Check if valid base64 key
        if key and key != "REPLACE_WITH_BASE64_32BYTE_KEY":
            # Test key validity
            return Fernet(key.encode("utf-8"))
    except Exception:
        pass

    # Deterministic fallback key derived from jwt_secret for development
    derived_bytes = hashlib.sha256(settings.jwt_secret.encode("utf-8")).digest()
    fallback_key = base64.urlsafe_b64encode(derived_bytes)
    return Fernet(fallback_key)


_fernet_instance: Fernet | None = None


def get_fernet() -> Fernet:
    global _fernet_instance
    if _fernet_instance is None:
        _fernet_instance = _get_fernet()
    return _fernet_instance


def encrypt_field(plaintext: str | None) -> str | None:
    """Encrypt plaintext to Fernet ciphertext string. Returns None if input is None."""
    if not plaintext:
        return plaintext
    fernet = get_fernet()
    encrypted_bytes = fernet.encrypt(plaintext.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")


def decrypt_field(ciphertext: str | None) -> str | None:
    """Decrypt Fernet ciphertext string to plaintext. Returns None if input is None."""
    if not ciphertext:
        return ciphertext
    fernet = get_fernet()
    try:
        decrypted_bytes = fernet.decrypt(ciphertext.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except Exception:
        # If decryption fails (e.g. invalid key or unencrypted legacy data), return raw string
        return ciphertext
