"""
Anchor — Health & Readiness Deployment Unit Tests.
"""

from __future__ import annotations

import unittest
from app.ai.classifier import SafetyClassifier


class TestHealthAndDeployment(unittest.TestCase):
    def setUp(self) -> None:
        self.classifier = SafetyClassifier()

    def test_health_classifier_probe(self) -> None:
        """Verify safety classifier probe returns None on neutral input."""
        res = self.classifier.deterministic_pre_filter("Hello world, today is a good day.")
        self.assertIsNone(res)

    def test_health_probe_payload_includes_version_and_uptime(self) -> None:
        """Health helper should expose version, env, and non-negative uptime."""
        from app.api.v1.health import _probe_payload, _uptime_seconds
        from app.core.config import settings

        payload = _probe_payload(alive=True)
        self.assertEqual(payload["service"], settings.app_name)
        self.assertEqual(payload["version"], settings.app_version)
        self.assertEqual(payload["env"], settings.app_env)
        self.assertTrue(payload["alive"])
        self.assertGreaterEqual(_uptime_seconds(), 0)
        self.assertIn("timestamp", payload)

    def test_dockerfile_and_ci_files_exist(self) -> None:
        """Verify Dockerfile and docker-compose.yml exist."""
        import os
        from pathlib import Path

        root_dir = Path(__file__).resolve().parents[2]
        self.assertTrue((root_dir / "Dockerfile").exists())
        self.assertTrue((root_dir / "docker-compose.yml").exists())
        self.assertTrue((root_dir / ".github" / "workflows" / "ci.yml").exists())


class _FakeClient:
    def __init__(self, host: str) -> None:
        self.host = host


class _FakeRequest:
    def __init__(self, headers: dict | None = None, host: str | None = None) -> None:
        self.headers = headers or {}
        self.client = _FakeClient(host) if host else None


class TestClientIpResolution(unittest.TestCase):
    def test_prefers_first_forwarded_hop(self) -> None:
        from app.core.rate_limit import _client_ip

        request = _FakeRequest(
            headers={"x-forwarded-for": "203.0.113.10, 10.0.0.1"},
            host="127.0.0.1",
        )
        self.assertEqual(_client_ip(request), "203.0.113.10")

    def test_falls_back_to_direct_client(self) -> None:
        from app.core.rate_limit import _client_ip

        request = _FakeRequest(host="192.0.2.20")
        self.assertEqual(_client_ip(request), "192.0.2.20")

    def test_unknown_when_no_client(self) -> None:
        from app.core.rate_limit import _client_ip

        request = _FakeRequest()
        self.assertEqual(_client_ip(request), "unknown")


if __name__ == "__main__":
    unittest.main()
