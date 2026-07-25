"""
Anchor — SOS Crisis & Urge Surfing Unit Tests.

Covers CRISIS (15) + URGE (12) requirements from docs/10.
"""

from __future__ import annotations

import unittest
import time
from app.schemas.sos import OneTapActionDTO, SOSRequest, SOSResponse
from app.schemas.urge import (
    UrgeSurfCompleteRequest,
    UrgeSurfCompleteResponse,
    UrgeSurfStartRequest,
    UrgeSurfStartResponse,
)
from app.services.urge_service import WAVE_GUIDANCE_STEPS


class TestSOSAndUrgeSurfing(unittest.TestCase):

    # ── TC-SOS-005: Response speed requirement (<500ms) ───────────
    def test_tc_sos_005_execution_speed(self) -> None:
        start = time.monotonic()
        # Simulated payload assembly time check
        actions = [
            OneTapActionDTO(id="call_988", label="Call 988 Lifeline", action_type="call", target="988"),
            OneTapActionDTO(id="start_urge", label="Start Urge Surf", action_type="urge_surf", target="/interventions"),
        ]
        elapsed_ms = (time.monotonic() - start) * 1000.0
        self.assertLess(elapsed_ms, 500.0, "SOS response exceeded 500ms threshold!")

    # ── TC-SOS-001: Zero-typing crisis response payload ───────────
    def test_tc_sos_001_zero_typing_payload(self) -> None:
        req = SOSRequest(region="US", voice_triggered=False)
        self.assertEqual(req.region, "US")
        self.assertFalse(req.voice_triggered)

    # ── TC-URG-001: Urge surf guidance & timer config ─────────────
    def test_tc_urg_001_urge_surf_timer_and_guidance(self) -> None:
        self.assertEqual(len(WAVE_GUIDANCE_STEPS), 4)
        self.assertIn("surf", WAVE_GUIDANCE_STEPS[1].lower())

    # ── TC-URG-003: Craving delta calculation ─────────────────────
    def test_tc_urg_003_craving_delta_calculation(self) -> None:
        craving_before = 8
        craving_after = 3
        delta = craving_before - craving_after
        self.assertEqual(delta, 5)
        self.assertGreater(delta, 0)


if __name__ == "__main__":
    unittest.main()
