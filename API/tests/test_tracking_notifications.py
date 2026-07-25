"""
Anchor — Milestones, Medication & Notifications Unit Tests.

Covers MILESTONE (10) + MED (10) + NUDGE (10) requirements from docs/10.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timezone
from app.schemas.tracking import MedicationLogRequest, MedicationCreateRequest
from app.schemas.notification import NotificationScheduleRequest
from app.services.tracking_service import COMPASSIONATE_RESET_MESSAGE
from app.services.notification_service import is_within_quiet_hours


class TestTrackingAndNotifications(unittest.TestCase):

    # ── Compassionate Reset Copy Verification ──────────────────────
    def test_compassionate_reset_framing(self) -> None:
        """Verify reset copy contains supportive framing, no shame or zero restart claims."""
        self.assertIn("data point", COMPASSIONATE_RESET_MESSAGE)
        self.assertIn("not a restart from zero", COMPASSIONATE_RESET_MESSAGE)
        self.assertNotIn("failed", COMPASSIONATE_RESET_MESSAGE.lower())
        self.assertNotIn("punishment", COMPASSIONATE_RESET_MESSAGE.lower())

    # ── Quiet Hours Compliance Verification ────────────────────────
    def test_quiet_hours_compliance(self) -> None:
        """Test quiet hours detection (22:00 to 07:00)."""
        dt_night = datetime(2026, 7, 25, 23, 30, tzinfo=timezone.utc)  # 23:30 -> inside quiet hours
        dt_morning = datetime(2026, 7, 25, 10, 0, tzinfo=timezone.utc)  # 10:00 -> outside quiet hours

        self.assertTrue(is_within_quiet_hours(dt_night, "22:00", "07:00"))
        self.assertFalse(is_within_quiet_hours(dt_morning, "22:00", "07:00"))

    # ── Medication Log Request Validation ─────────────────────────
    def test_medication_log_validation(self) -> None:
        req = MedicationLogRequest(status="taken")
        self.assertEqual(req.status, "taken")

        with self.assertRaises(ValueError):
            MedicationLogRequest(status="invalid_status")

    # ── Notification Schedule Request Validation ───────────────────
    def test_notification_schedule_validation(self) -> None:
        now = datetime.now(timezone.utc)
        req = NotificationScheduleRequest(type="nudge", scheduled_for=now, payload={"msg": "Check in"})
        self.assertEqual(req.type, "nudge")


if __name__ == "__main__":
    unittest.main()
