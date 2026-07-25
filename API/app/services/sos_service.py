"""
Anchor — Zero-Typing SOS Crisis Service.

Delivers zero-typing crisis response in <500ms:
  - Resolves emergency contacts for user (decrypting phone numbers)
  - Resolves region crisis line (988 US / KIRAN IN / Generic)
  - Assembles one-tap action buttons (call guardian, call sponsor, call 988, urge surf)
  - Audits safety event to safety_events table
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import decrypt_field
from app.models.safety import SafetyEvent
from app.repositories.audit_repo import AuditRepository
from app.repositories.user_repo import UserRepository
from app.schemas.sos import OneTapActionDTO, SOSRequest, SOSResponse
from app.services.safety_service import SafetyService


class SOSService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.audit_repo = AuditRepository(session)
        self.safety_service = SafetyService(session)

    async def trigger_sos(self, user_id: uuid.UUID, req: SOSRequest) -> SOSResponse:
        start_time = time.monotonic()

        # Get region resources
        region = req.region or "US"
        resources = self.safety_service.get_region_resources(region)
        primary_resource = resources[0] if resources else {
            "name": "988 Crisis Lifeline",
            "phone": "988",
            "description": "Free, confidential 24/7 support"
        }

        # Resolve emergency contacts (decrypting phone numbers for authorized owner)
        raw_contacts = await self.user_repo.get_emergency_contacts(user_id)
        decrypted_contacts: List[Dict[str, str]] = []
        one_tap_actions: List[OneTapActionDTO] = []

        sponsor_contact = None
        guardian_contact = None

        for c in raw_contacts:
            phone_plain = decrypt_field(c.phone_ciphertext) or ""
            decrypted_contacts.append({
                "name": c.name,
                "relationship": c.relationship,
                "phone": phone_plain,
                "is_sponsor": c.is_sponsor,
            })
            if c.is_sponsor and not sponsor_contact:
                sponsor_contact = (c.name, phone_plain)
            elif not guardian_contact:
                guardian_contact = (c.name, phone_plain)

        # Build one-tap actions
        if sponsor_contact:
            one_tap_actions.append(
                OneTapActionDTO(
                    id="call_sponsor",
                    label=f"Call Sponsor ({sponsor_contact[0]})",
                    action_type="call",
                    target=sponsor_contact[1],
                )
            )

        if guardian_contact:
            one_tap_actions.append(
                OneTapActionDTO(
                    id="call_guardian",
                    label=f"Call Guardian ({guardian_contact[0]})",
                    action_type="call",
                    target=guardian_contact[1],
                )
            )

        # Always add region crisis line action
        crisis_phone = primary_resource.get("phone", "988")
        one_tap_actions.append(
            OneTapActionDTO(
                id="call_crisis_line",
                label=f"Call {primary_resource['name']} ({crisis_phone})",
                action_type="call",
                target=crisis_phone,
            )
        )

        # Always add urge surfing action
        one_tap_actions.append(
            OneTapActionDTO(
                id="start_urge_surf",
                label="Start 4-Minute Guided Urge Surf",
                action_type="urge_surf",
                target="/interventions/urge-surf/start",
            )
        )

        # Audit crisis safety event
        safety_event = SafetyEvent(
            user_id=user_id,
            label="crisis",
            confidence=1.0,
            action_taken="zero_typing_sos_triggered",
            resource_shown=primary_resource["name"],
            tier=4,
        )
        await self.audit_repo.log_safety_event(safety_event)

        response_text = (
            "We are here with you right now. Your safety and well-being come first. "
            "Please connect with human support using the one-tap options below."
        )

        elapsed_ms = (time.monotonic() - start_time) * 1000.0

        return SOSResponse(
            response_text=response_text,
            crisis_line=primary_resource,
            emergency_contacts=decrypted_contacts,
            one_tap_actions=one_tap_actions,
            timestamp=datetime.now(timezone.utc),
        )
