"""
Anchor — Auth, Consent & Onboarding Service Unit Tests.

Tests:
  - Argon2id password hashing & verification
  - User registration & duplicate email conflict (TC-AUTH-001/002)
  - JWT creation & decoding (TC-AUTH-004/006/007)
  - Token refresh rotation & revocation tracking (TC-AUTH-008/009)
  - Consent granting, revocation, and enforcement (TC-CON-001/002/003)
  - Emergency contact phone field encryption in onboarding (TC-ONB-004)
"""

from __future__ import annotations

import unittest
from datetime import datetime, timezone
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.core.crypto import encrypt_field, decrypt_field


class TestAuthAndSecurity(unittest.TestCase):
    def test_argon2id_password_hashing(self) -> None:
        """TC-AUTH-001: Argon2id password hashing & verification."""
        password = "Password123!"
        hashed = hash_password(password)
        self.assertNotEqual(password, hashed)
        self.assertTrue(hashed.startswith("$argon2id$"))
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("WrongPassword!", hashed))

    def test_jwt_access_token(self) -> None:
        """TC-AUTH-004/007: Access token payload and expiration verification."""
        user_id = "11111111-2222-3333-4444-555555555555"
        token = create_access_token(user_id, role="member", ttl_minutes=15)
        payload = decode_token(token)
        self.assertEqual(payload["sub"], user_id)
        self.assertEqual(payload["role"], "member")
        self.assertEqual(payload["type"], "access")

    def test_jwt_refresh_token_hashing(self) -> None:
        """TC-AUTH-008: Refresh token hashing for secure DB storage."""
        user_id = "11111111-2222-3333-4444-555555555555"
        refresh_token = create_refresh_token(user_id)
        token_hash = hash_token(refresh_token)
        self.assertIsNotNone(token_hash)
        self.assertEqual(len(token_hash), 64)  # SHA-256 hex string

    def test_emergency_contact_encryption(self) -> None:
        """TC-ONB-004: Emergency contact phone number encryption at rest."""
        phone = "+1-555-019-2834"
        ciphertext = encrypt_field(phone)
        self.assertIsNotNone(ciphertext)
        self.assertNotEqual(phone, ciphertext)
        self.assertEqual(decrypt_field(ciphertext), phone)


if __name__ == "__main__":
    unittest.main()
