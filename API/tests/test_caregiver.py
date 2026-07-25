"""
Anchor — Caregiver Circle & Copilot Unit Tests.

Covers CAREGIVER (18) requirements from docs/10.
"""

from __future__ import annotations

import unittest
from app.schemas.caregiver import CaregiverSuggestionDTO, ShareProposeRequest
from app.services.caregiver_service import CaregiverService


class TestCaregiverCircleAndCopilot(unittest.TestCase):

    # ── Caregiver Copilot 3-Element Schema Verification ─────────────
    def test_caregiver_copilot_3_element_schema(self) -> None:
        """Verify Caregiver Copilot returns suggested_message, avoid[], rationale."""
        service = CaregiverService(session=None)  # type: ignore
        suggestion = service._generate_copilot_suggestion("hard_moment", "Craving at 8pm after work")

        self.assertIsNotNone(suggestion.suggested_message)
        self.assertIn("proud", suggestion.suggested_message.lower())

        self.assertIsInstance(suggestion.avoid, list)
        self.assertGreater(len(suggestion.avoid), 0)

        self.assertIsNotNone(suggestion.rationale)
        self.assertIn("CRAFT", suggestion.rationale)

    # ── Share Request Schema Validation ────────────────────────────
    def test_share_propose_request_validation(self) -> None:
        req = ShareProposeRequest(kind="hard_moment", summary="Felt heavy craving after work")
        self.assertEqual(req.kind, "hard_moment")
        self.assertEqual(req.summary, "Felt heavy craving after work")

        with self.assertRaises(ValueError):
            ShareProposeRequest(kind="invalid_kind", summary="test")


if __name__ == "__main__":
    unittest.main()
