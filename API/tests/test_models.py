"""
Anchor — Model & Constraint Unit Tests.

Tests:
  - TC-CHK-002: Craving range validation (0-10)
  - TC-CHK-003: Mood range validation (1-5)
  - TC-RISK-001: Risk score range validation (0-100)
  - TC-CAR-018: Unique active caregiver pair constraint definition
  - Field-level encryption & decryption roundtrip
"""

from __future__ import annotations

import unittest
from app.core.crypto import decrypt_field, encrypt_field
from app.models.checkin import CheckIn
from app.models.risk import RiskScore
from app.models.caregiver import CaregiverLink


class TestCryptoAndModels(unittest.TestCase):
    def test_field_encryption_roundtrip(self) -> None:
        """Verify encrypt_field and decrypt_field work symmetrically."""
        original = "Secret recovery note: felt anxious at 8pm"
        ciphertext = encrypt_field(original)
        self.assertIsNotNone(ciphertext)
        self.assertNotEqual(ciphertext, original)
        decrypted = decrypt_field(ciphertext)
        self.assertEqual(decrypted, original)

    def test_field_encryption_none_handling(self) -> None:
        """Verify encryption helpers handle None/empty values cleanly."""
        self.assertIsNone(encrypt_field(None))
        self.assertIsNone(decrypt_field(None))
        self.assertEqual(encrypt_field(""), "")
        self.assertEqual(decrypt_field(""), "")

    def test_checkin_valid_instantiation(self) -> None:
        """Verify CheckIn instantiates cleanly within valid ranges."""
        checkin = CheckIn(
            mood=3,
            sleep_quality=4,
            craving=5,
            halt_hungry=True,
        )
        self.assertEqual(checkin.mood, 3)
        self.assertEqual(checkin.sleep_quality, 4)
        self.assertEqual(checkin.craving, 5)

    def test_checkin_table_args(self) -> None:
        """Verify CheckIn has mood, sleep, craving CHECK constraints defined."""
        constraints = [arg.name for arg in CheckIn.__table_args__ if hasattr(arg, 'name')]
        self.assertIn("chk_checkin_mood_range", constraints)
        self.assertIn("chk_checkin_sleep_range", constraints)
        self.assertIn("chk_checkin_craving_range", constraints)

    def test_risk_score_valid_instantiation(self) -> None:
        """Verify RiskScore instantiates cleanly within valid range 0-100."""
        risk = RiskScore(
            score=75,
            band="elevated",
            factors=[{"factor": "craving_trend", "impact": "+20"}],
        )
        self.assertEqual(risk.score, 75)
        self.assertEqual(risk.band, "elevated")

    def test_risk_score_table_args(self) -> None:
        """Verify RiskScore has score CHECK constraint defined."""
        constraints = [arg.name for arg in RiskScore.__table_args__ if hasattr(arg, 'name')]
        self.assertIn("chk_risk_score_range", constraints)

    def test_caregiver_link_table_args(self) -> None:
        """Verify CaregiverLink has uq_active_caregiver_link index defined."""
        indexes = [arg.name for arg in CaregiverLink.__table_args__ if hasattr(arg, 'name')]
        self.assertIn("uq_active_caregiver_link", indexes)


if __name__ == "__main__":
    unittest.main()
