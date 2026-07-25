"""
Anchor — Safety Subsystem Service & Escalation Engine.

Implements:
  - Deterministic safety classification & severity raiser
  - Crisis short-circuit (bypasses LLM freestyle generation)
  - Escalation ladder tier calculation (Tiers 0-5)
  - Region crisis resource resolution (US, IN, GENERIC)
  - Audit logging to safety_events table (minimized fields, no raw crisis text over-stored)
"""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.classifier import ClassificationResult, SafetyClassifier, SafetyLabel
from app.ai.prompts import prompt_loader
from app.core.config import settings
from app.models.safety import SafetyEvent
from app.repositories.audit_repo import AuditRepository


# ── Escalation Ladder Tiers (docs/08 §1.3) ──────────────────────
# Tier 0: Self-help / psychoeducation
# Tier 1: Coping tool (urge-surf, grounding)
# Tier 2: Peer / sponsor
# Tier 3: Guardian (consented alert + Copilot)
# Tier 4: Crisis line (region resource, one-tap)
# Tier 5: Emergency services


def calculate_escalation_tier(label: SafetyLabel, steady_band: str = "low") -> int:
    """Calculate appropriate escalation tier based on safety label and Steady Score band."""
    if label in (SafetyLabel.CRISIS, SafetyLabel.SELF_HARM, SafetyLabel.HARM_TO_OTHERS, SafetyLabel.MEDICAL_EMERGENCY):
        return 4 if label != SafetyLabel.MEDICAL_EMERGENCY else 5
    elif label == SafetyLabel.DISTRESS:
        if steady_band in ("elevated", "high"):
            return 3  # Suggest guardian / coping tool
        return 1      # Suggest coping tool (urge surf / grounding)
    return 0


class SafetyService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.classifier = SafetyClassifier()
        self.audit_repo = AuditRepository(session)

    def get_region_resources(self, region: str | None = None) -> List[Dict[str, Any]]:
        """Load region-appropriate crisis resources."""
        target_region = (region or settings.crisis_default_region).upper()
        rel_path = f"crisis.templates/resources_{target_region}.json"

        try:
            content = prompt_loader.get_prompt(rel_path)
            data = json.loads(content)
            return data.get("resources", [])
        except Exception:
            # Fallback to generic resources
            try:
                content = prompt_loader.get_prompt("crisis.templates/resources_GENERIC.json")
                return json.loads(content).get("resources", [])
            except Exception:
                return [
                    {
                        "name": "Local Emergency Services",
                        "description": "Call local emergency number (911/112/999) or contact a trusted person.",
                    }
                ]

    async def classify_and_route(
        self,
        user_id: uuid.UUID,
        text: str,
        conversation_id: Optional[uuid.UUID] = None,
        region: Optional[str] = None,
        steady_band: str = "low",
    ) -> Dict[str, Any]:
        """
        Main Safety Subsystem Pipeline:
        1. Classify inbound text.
        2. Calculate escalation tier.
        3. If crisis/self_harm/harm/medical -> SHORT-CIRCUIT AI generation.
        4. Audit safety event to DB.
        5. Return response envelope + one-tap actions.
        """
        classification: ClassificationResult = await self.classifier.classify(text)
        label = classification.label
        tier = calculate_escalation_tier(label, steady_band)

        # Check if crisis short-circuit applies
        is_short_circuit = label in (
            SafetyLabel.CRISIS,
            SafetyLabel.SELF_HARM,
            SafetyLabel.HARM_TO_OTHERS,
            SafetyLabel.MEDICAL_EMERGENCY,
        )

        resources = self.get_region_resources(region)
        action_taken = "crisis_short_circuit" if is_short_circuit else "normal_routing"
        primary_resource = resources[0]["name"] if resources else None

        # Audit safety event to database (minimized fields, no raw crisis text over-stored)
        safety_event = SafetyEvent(
            user_id=user_id,
            conversation_id=conversation_id,
            label=label.value,
            confidence=classification.confidence,
            action_taken=action_taken,
            resource_shown=primary_resource,
            tier=tier,
        )
        await self.audit_repo.log_safety_event(safety_event)

        # Build response payload
        crisis_template_text = None
        actions = []

        if is_short_circuit:
            # Load fixed human-reviewed crisis template
            crisis_template_text = prompt_loader.get_prompt("crisis.templates/crisis_response.md")
            actions = [
                {"id": "urge_surf", "label": "Ride it out with me (Urge Surf)"},
                {"id": "call_guardian", "label": "Call Guardian / Support Person"},
                {"id": "crisis_line", "label": resources[0]["name"], "phone": resources[0].get("phone", "988")},
            ]

        return {
            "safety_label": label.value,
            "confidence": classification.confidence,
            "signals": classification.signals,
            "tier": tier,
            "short_circuit": is_short_circuit,
            "crisis_response": crisis_template_text,
            "resources": resources,
            "actions": actions,
        }
