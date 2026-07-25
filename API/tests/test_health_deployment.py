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

    def test_dockerfile_and_ci_files_exist(self) -> None:
        """Verify Dockerfile and docker-compose.yml exist."""
        import os
        from pathlib import Path

        root_dir = Path(__file__).resolve().parents[2]
        self.assertTrue((root_dir / "Dockerfile").exists())
        self.assertTrue((root_dir / "docker-compose.yml").exists())
        self.assertTrue((root_dir / ".github" / "workflows" / "ci.yml").exists())


if __name__ == "__main__":
    unittest.main()
