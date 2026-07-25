"""
Anchor — Onboarding & Profile Service.

Handles <90s onboarding, profile management, emergency contacts (with field encryption), and triggers.
"""

from __future__ import annotations

import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import decrypt_field, encrypt_field
from app.core.exceptions import NotFoundError
from app.models.profile import EmergencyContact, MemberProfile, Trigger
from app.repositories.user_repo import UserRepository
from app.schemas.onboarding import (
    EmergencyContactRequest,
    EmergencyContactResponse,
    OnboardingSubmitRequest,
    ProfileUpdateRequest,
    TriggerRequest,
)


class OnboardingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def submit_onboarding(
        self, user_id: uuid.UUID, req: OnboardingSubmitRequest
    ) -> MemberProfile:
        profile = await self.user_repo.get_profile(user_id)
        if not profile:
            profile = MemberProfile(user_id=user_id)

        profile.recovery_goal = req.recovery_goal
        profile.substance_focus = req.substance_focus
        profile.recovery_start_date = req.recovery_start_date
        profile.region = req.region
        profile.voice_first = req.voice_first
        profile.quiet_hours_start = req.quiet_hours_start
        profile.quiet_hours_end = req.quiet_hours_end

        await self.user_repo.save_profile(profile)

        # Add emergency contact if provided
        if req.emergency_contact:
            await self.add_emergency_contact(user_id, req.emergency_contact)

        # Add triggers if provided
        for trigger_req in req.triggers:
            await self.add_trigger(user_id, trigger_req)

        return profile

    async def get_profile(self, user_id: uuid.UUID) -> MemberProfile:
        profile = await self.user_repo.get_profile(user_id)
        if not profile:
            # Create default profile if not present
            profile = MemberProfile(user_id=user_id)
            await self.user_repo.save_profile(profile)
        return profile

    async def update_profile(
        self, user_id: uuid.UUID, req: ProfileUpdateRequest
    ) -> MemberProfile:
        profile = await self.get_profile(user_id)
        for field, value in req.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
        await self.user_repo.save_profile(profile)
        return profile

    async def add_emergency_contact(
        self, user_id: uuid.UUID, req: EmergencyContactRequest
    ) -> EmergencyContactResponse:
        contact = EmergencyContact(
            user_id=user_id,
            name=req.name,
            relationship=req.relationship,
            phone_ciphertext=encrypt_field(req.phone) or "",
            is_sponsor=req.is_sponsor,
            priority=req.priority,
        )
        await self.user_repo.add_emergency_contact(contact)
        return EmergencyContactResponse(
            id=contact.id,
            name=contact.name,
            relationship=contact.relationship,
            phone=req.phone,
            is_sponsor=contact.is_sponsor,
            priority=contact.priority,
        )

    async def get_emergency_contacts(
        self, user_id: uuid.UUID
    ) -> Sequence[EmergencyContactResponse]:
        contacts = await self.user_repo.get_emergency_contacts(user_id)
        result = []
        for c in contacts:
            decrypted_phone = decrypt_field(c.phone_ciphertext) or ""
            result.append(
                EmergencyContactResponse(
                    id=c.id,
                    name=c.name,
                    relationship=c.relationship,
                    phone=decrypted_phone,
                    is_sponsor=c.is_sponsor,
                    priority=c.priority,
                )
            )
        return result

    async def add_trigger(self, user_id: uuid.UUID, req: TriggerRequest) -> Trigger:
        trigger = Trigger(
            user_id=user_id,
            label=req.label,
            type=req.type,
            time_of_day=req.time_of_day,
            location_context=req.location_context,
        )
        self.session.add(trigger)
        await self.session.flush()
        return trigger
