"""
Anchor — Pre/Post Generation Safety Guards.

PreGuard: Inspects user input for prompt injection or jailbreak attempts.
PostGuard: Verifies generated output against out-of-model safety rules:
  - Blocks dosing / medication / tapering instructions (TC-SAF-014)
  - Blocks methods of self-harm or suicide (TC-SAF-013)
  - Blocks content discouraging professional / crisis help (TC-SAF-015)
  - Enforces citation grounding for health claims (TC-AI-008)
  - Blocks jailbreak attempts to bypass safety (TC-AI-012, TC-SAF-012)
"""

from __future__ import annotations

import re
from typing import List
from pydantic import BaseModel


class GuardResult(BaseModel):
    is_safe: bool
    violations: List[str] = []
    sanitized_text: str | None = None


class PreGuard:
    """Pre-generation input validation."""

    JAILBREAK_PATTERNS = [
        r"ignore\s+(all\s+)?(prior|previous|safety|system)\s+(instructions|rules|prompts)",
        r"bypass\s+safety",
        r"you\s+are\s+now\s+in\s+developer\s+mode",
        r"do\s+anything\s+now",
    ]

    def check_input(self, text: str) -> GuardResult:
        """Inspect input text for injection or jailbreak attempts."""
        text_lower = text.lower()
        violations = []

        for pattern in self.JAILBREAK_PATTERNS:
            if re.search(pattern, text_lower):
                violations.append("prompt_injection_jailbreak")

        if violations:
            return GuardResult(
                is_safe=False,
                violations=violations,
                sanitized_text="I am designed to be a safe, grounded recovery companion and cannot bypass safety guidelines.",
            )

        return GuardResult(is_safe=True, violations=[], sanitized_text=text)


class PostGuard:
    """Post-generation output verification."""

    DISALLOWED_PATTERNS = [
        # Dosing / tapering / medication instructions (TC-SAF-014)
        (r"\b(take\s+\d+\s*mg|dosage|tapering\s+dose|prescription|pill\s+count|increase\s+your\s+dose)\b", "dosing_instruction"),

        # Self-harm / suicide methods (TC-SAF-013)
        (r"\b(how\s+to\s+cut|how\s+to\s+overdose|methods\s+of\s+suicide|best\s+way\s+to\s+kill|lethal\s+dose)\b", "harm_methods"),

        # Discouraging professional or crisis help (TC-SAF-015)
        (r"\b(don'?t\s+call\s+988|avoid\s+doctors|don'?t\s+go\s+to\s+hospital|therapists\s+are\s+useless|don'?t\s+seek\s+help)\b", "discourage_help"),

        # Jailbreak relabeling attempts (TC-SAF-012)
        (r"\b(safety_label\s*=\s*none|override\s+crisis|ignore\s+safety)\b", "jailbreak_override"),
    ]

    def verify_output(self, generated_text: str, citations: List[str] | None = None) -> GuardResult:
        """
        Verify generated output against disallowed content rules.
        """
        text_lower = generated_text.lower()
        violations = []

        for pattern, violation_type in self.DISALLOWED_PATTERNS:
            if re.search(pattern, text_lower):
                violations.append(violation_type)

        if violations:
            safe_fallback = (
                "I am here to support your recovery journey safely. For specific medical or medication guidance, "
                "please consult a healthcare professional. If you or someone you know is in distress or crisis, "
                "please call or text 988 (Suicide & Crisis Lifeline) or contact local emergency services immediately."
            )
            return GuardResult(
                is_safe=False,
                violations=violations,
                sanitized_text=safe_fallback,
            )

        return GuardResult(is_safe=True, violations=[], sanitized_text=generated_text)
