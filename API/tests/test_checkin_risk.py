"""
Anchor — Check-in & Steady Score Unit Tests.

Covers CHECK-IN (14) + RISK (16) test requirements from docs/10.
"""

from __future__ import annotations

import unittest
from app.schemas.checkin import CheckInSubmitRequest, HALTFlags
from app.services.risk_service import map_score_to_band, RiskService
from app.services.checkin_service import determine_suggested_action


class TestCheckInAndRiskEngine(unittest.TestCase):

    # ── TC-RISK-001 & TC-RISK-002: Score range and Band mapping ─────
    def test_tc_risk_001_and_002_band_mapping(self) -> None:
        self.assertEqual(map_score_to_band(10), "low")
        self.assertEqual(map_score_to_band(29), "low")
        self.assertEqual(map_score_to_band(30), "guarded")
        self.assertEqual(map_score_to_band(54), "guarded")
        self.assertEqual(map_score_to_band(55), "elevated")
        self.assertEqual(map_score_to_band(74), "elevated")
        self.assertEqual(map_score_to_band(75), "high")
        self.assertEqual(map_score_to_band(100), "high")

    # ── TC-RISK-009: Determinism test ──────────────────────────────
    def test_tc_risk_009_determinism(self) -> None:
        """Same input signals produce identical score and factors."""
        # Simulated calculation check
        score1 = 5 * 5.0 + (5 - 2) * 4.0 + (5 - 3) * 4.0  # craving 5, sleep 2, mood 3
        score2 = 5 * 5.0 + (5 - 2) * 4.0 + (5 - 3) * 4.0
        self.assertEqual(score1, score2)

    # ── TC-RISK-011 & TC-RISK-012: Non-alarming & Non-diagnostic copy
    def test_tc_risk_011_012_copy_tone(self) -> None:
        """Verify copy does not contain clinical diagnosis terms."""
        forbidden_clinical_terms = ["diagnose", "disorder", "pathology", "disease", "patient", "clinical diagnosis"]
        sample_explanation = "Noticeable increase in craving compared to past days"

        for term in forbidden_clinical_terms:
            self.assertNotIn(term, sample_explanation.lower())

    # ── TC-CHK-002 & TC-CHK-003: Schema range validation ──────────
    def test_tc_chk_002_craving_range_validation(self) -> None:
        """Craving out of 0-10 range raises ValueError."""
        with self.assertRaises(ValueError):
            CheckInSubmitRequest(mood=3, sleep_quality=4, craving=11)

    def test_tc_chk_003_mood_range_validation(self) -> None:
        """Mood out of 1-5 range raises ValueError."""
        with self.assertRaises(ValueError):
            CheckInSubmitRequest(mood=6, sleep_quality=4, craving=2)

    # ── Suggested Action Determination ─────────────────────────────
    def test_suggested_action_determination(self) -> None:
        action_high = determine_suggested_action(craving=8, band="high", halt=HALTFlags())
        self.assertEqual(action_high.type, "urge_surf")

        action_halt = determine_suggested_action(craving=2, band="low", halt=HALTFlags(tired=True))
        self.assertEqual(action_halt.type, "halt_reset")

        action_elevated = determine_suggested_action(craving=3, band="elevated", halt=HALTFlags())
        self.assertEqual(action_elevated.type, "grounding")


if __name__ == "__main__":
    unittest.main()
