"""
Anchor — Caregiver Circle & Copilot Service.

Manages:
  - Caregiver link state machine (invited -> active -> revoked)
  - Partial unique index enforcement: max 1 active link per member (TC-CAR-018)
  - Moment sharing with dual-gate enforcement: requires active link AND active consent (TC-CAR-004)
  - Caregiver Copilot 3-element generator (suggested_message, avoid[], rationale)
  - Guardian feed retrieval
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import decrypt_field, encrypt_field
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.caregiver import CaregiverLink, CaregiverSuggestion, ShareEvent
from app.repositories.caregiver_repo import CaregiverRepository
from app.repositories.consent_repo import ConsentRepository
from app.repositories.user_repo import UserRepository
from app.schemas.caregiver import (
    CaregiverInviteRequest,
    CaregiverLinkResponse,
    CaregiverSuggestionDTO,
    ShareEventResponse,
    ShareProposeRequest,
)


class CaregiverService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.caregiver_repo = CaregiverRepository(session)
        self.consent_repo = ConsentRepository(session)
        self.user_repo = UserRepository(session)

    async def invite_caregiver(
        self, member_id: uuid.UUID, req: CaregiverInviteRequest
    ) -> CaregiverLinkResponse:
        guardian = await self.user_repo.get_by_email(req.guardian_email)
        if not guardian:
            raise NotFoundError("Guardian account not found. Guardian must register first.")

        if guardian.id == member_id:
            raise ConflictError("Cannot link yourself as your own caregiver.")

        # Check if active link already exists for member (TC-CAR-018)
        active_link = await self.caregiver_repo.get_active_link_for_member(member_id)
        if active_link:
            raise ConflictError("Member already has an active caregiver link. Revoke existing link before creating a new one.")

        link = CaregiverLink(
            member_id=member_id,
            guardian_id=guardian.id,
            status="invited",
            invited_at=datetime.now(timezone.utc),
        )
        await self.caregiver_repo.create_link(link)
        return CaregiverLinkResponse.model_validate(link)

    async def accept_invite(
        self, guardian_id: uuid.UUID, link_id: uuid.UUID
    ) -> CaregiverLinkResponse:
        link = await self.caregiver_repo.get_link_by_id(link_id)
        if not link or link.guardian_id != guardian_id:
            raise NotFoundError("Caregiver link invitation not found.")

        if link.status == "active":
            return CaregiverLinkResponse.model_validate(link)

        # Enforce max 1 active link per member
        existing_active = await self.caregiver_repo.get_active_link_for_member(link.member_id)
        if existing_active and existing_active.id != link.id:
            raise ConflictError("Member already has another active caregiver link.")

        link.status = "active"
        link.accepted_at = datetime.now(timezone.utc)
        return CaregiverLinkResponse.model_validate(link)

    async def revoke_link(self, user_id: uuid.UUID) -> None:
        # Check active link as member or guardian
        active_link = await self.caregiver_repo.get_active_link_for_member(user_id)
        if active_link:
            active_link.status = "revoked"
            active_link.revoked_at = datetime.now(timezone.utc)

    async def propose_share(
        self, member_id: uuid.UUID, req: ShareProposeRequest
    ) -> ShareEventResponse:
        # ── Gate 1: Check active caregiver link exists ─────────────────
        active_link = await self.caregiver_repo.get_active_link_for_member(member_id)
        if not active_link or active_link.status != "active":
            raise ForbiddenError("Sharing blocked: No active caregiver link found. Member must link with a guardian first.")

        # ── Gate 2: Check active share_with_guardian consent (TC-CAR-004) ─
        has_consent = await self.consent_repo.has_active_consent(member_id, "share_with_guardian")
        if not has_consent:
            raise ForbiddenError("Sharing blocked: Member has not granted active consent to share with caregiver.")

        guardian_id = active_link.guardian_id
        summary_cipher = encrypt_field(req.summary) or ""

        # Create ShareEvent
        share_event = ShareEvent(
            member_id=member_id,
            guardian_id=guardian_id,
            kind=req.kind,
            summary_ciphertext=summary_cipher,
        )
        await self.caregiver_repo.create_share_event(share_event)

        # Generate Caregiver Copilot 3-element guidance
        suggestion_dto = self._generate_copilot_suggestion(req.kind, req.summary)

        suggestion_entity = CaregiverSuggestion(
            share_event_id=share_event.id,
            suggested_message=suggestion_dto.suggested_message,
            avoid=suggestion_dto.avoid,
            rationale=suggestion_dto.rationale,
        )
        await self.caregiver_repo.save_suggestion(suggestion_entity)

        return ShareEventResponse(
            id=share_event.id,
            member_id=member_id,
            guardian_id=guardian_id,
            kind=req.kind,
            summary=req.summary,
            suggestion=suggestion_dto,
            created_at=share_event.created_at,
        )

    def _generate_copilot_suggestion(self, kind: str, summary: str) -> CaregiverSuggestionDTO:
        """Generates 3 supportive communication elements for the caregiver (Copilot)."""
        if kind == "hard_moment":
            return CaregiverSuggestionDTO(
                suggested_message="I love you and I am proud of you for working through this hard moment. I am here whenever you want to talk.",
                avoid=[
                    "Do not interrogate about what triggered the craving",
                    "Do not express panic or anger",
                    "Do not lecture about past mistakes",
                ],
                rationale="CRAFT principles recommend calm, non-judgmental presence that validates effort without demanding explanations.",
            )
        elif kind == "milestone":
            return CaregiverSuggestionDTO(
                suggested_message="Congratulations on reaching this milestone! Watching your dedication is truly inspiring.",
                avoid=[
                    "Do not minimize the milestone",
                    "Do not warn 'don't ruin it now'",
                ],
                rationale="Positive reinforcement strengthens self-efficacy and long-term recovery resilience.",
            )
        else:
            return CaregiverSuggestionDTO(
                suggested_message="Thank you for sharing your update with me. Sending warmth and support for your day.",
                avoid=["Avoid intrusive questioning"],
                rationale="Consistent, calm affirmation maintains open trust channels between member and caregiver.",
            )

    async def get_guardian_feed(
        self, guardian_id: uuid.UUID, limit: int = 20
    ) -> List[ShareEventResponse]:
        events = await self.caregiver_repo.get_guardian_feed(guardian_id, limit)
        result = []
        for e in events:
            # Check if member still has active consent before showing feed item!
            has_consent = await self.consent_repo.has_active_consent(e.member_id, "share_with_guardian")
            if not has_consent:
                continue  # Revoked consent suppresses feed visibility

            plain_summary = decrypt_field(e.summary_ciphertext) or ""
            suggestion_dto = None
            if e.suggestion:
                suggestion_dto = CaregiverSuggestionDTO(
                    suggested_message=e.suggestion.suggested_message,
                    avoid=e.suggestion.avoid,
                    rationale=e.suggestion.rationale,
                )

            result.append(
                ShareEventResponse(
                    id=e.id,
                    member_id=e.member_id,
                    guardian_id=e.guardian_id,
                    kind=e.kind,
                    summary=plain_summary,
                    suggestion=suggestion_dto,
                    created_at=e.created_at,
                )
            )
        return result
