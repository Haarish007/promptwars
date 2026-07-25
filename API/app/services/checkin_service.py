"""
Anchor — Check-in Service.

Manages check-in submissions, note encryption at rest, Steady Score recomputation,
and tailored micro-intervention recommendations.
"""

from __future__ import annotations

import uuid
from typing import List, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import decrypt_field, encrypt_field
from app.models.checkin import CheckIn
from app.models.risk import RiskScore
from app.repositories.checkin_repo import CheckInRepository
from app.repositories.risk_repo import RiskRepository
from app.schemas.checkin import (
    CheckInResponse,
    CheckInSubmitRequest,
    CheckInSubmitResponse,
    HALTFlags,
    SuggestedActionDTO,
)
from app.services.risk_service import RiskService


def determine_suggested_action(craving: int, band: str, halt: HALTFlags) -> SuggestedActionDTO:
    """Recommend an evidence-based micro-intervention based on check-in signals."""
    if craving >= 7 or band == "high":
        return SuggestedActionDTO(
            type="urge_surf",
            label="Ride out the craving with a 4-minute urge surfing session",
        )
    elif halt.tired or halt.lonely or halt.angry or halt.hungry:
        return SuggestedActionDTO(
            type="halt_reset",
            label="Take a 2-minute HALT sensory grounding reset",
        )
    elif band in ("elevated", "guarded"):
        return SuggestedActionDTO(
            type="grounding",
            label="5-4-3-2-1 Grounding exercise",
        )
    return SuggestedActionDTO(
        type="connect",
        label="Log a daily milestone or check in with your support circle",
    )


class CheckInService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.checkin_repo = CheckInRepository(session)
        self.risk_repo = RiskRepository(session)
        self.risk_service = RiskService(session)

    async def submit_checkin(
        self, user_id: uuid.UUID, req: CheckInSubmitRequest
    ) -> CheckInSubmitResponse:
        # Encrypt free-text note at rest
        note_cipher = encrypt_field(req.note) if req.note else None

        checkin = CheckIn(
            user_id=user_id,
            mood=req.mood,
            sleep_quality=req.sleep_quality,
            craving=req.craving,
            halt_hungry=req.halt.hungry,
            halt_angry=req.halt.angry,
            halt_lonely=req.halt.lonely,
            halt_tired=req.halt.tired,
            note_ciphertext=note_cipher,
            source=req.source,
        )
        await self.checkin_repo.create(checkin)

        # Get recent check-ins for trend comparison
        recent_checkins = await self.checkin_repo.get_user_history(user_id, limit=5)

        # Recompute Steady Score
        risk_res = await self.risk_service.compute_score(
            user_id=user_id,
            current_checkin=checkin,
            recent_checkins=recent_checkins[1:],  # Exclude current checkin
        )

        # Save risk score snapshot
        score_entity = RiskScore(
            user_id=user_id,
            score=risk_res.score,
            band=risk_res.band,
            factors=[f.model_dump() for f in risk_res.factors],
            checkin_id=checkin.id,
        )
        await self.risk_repo.save_score(score_entity)
        risk_res.id = score_entity.id
        risk_res.created_at = score_entity.created_at

        # Determine suggested action
        suggested_action = determine_suggested_action(
            req.craving, risk_res.band, req.halt
        )

        checkin_dto = CheckInResponse(
            id=checkin.id,
            mood=checkin.mood,
            sleep_quality=checkin.sleep_quality,
            craving=checkin.craving,
            halt=req.halt,
            note=req.note,
            source=checkin.source,
            created_at=checkin.created_at,
        )

        return CheckInSubmitResponse(
            checkin=checkin_dto,
            risk=risk_res.model_dump(),
            suggested_action=suggested_action,
        )

    async def get_checkin_trend(
        self, user_id: uuid.UUID, limit: int = 30
    ) -> List[CheckInResponse]:
        checkins = await self.checkin_repo.get_user_history(user_id, limit)
        result = []
        for c in checkins:
            decrypted_note = decrypt_field(c.note_ciphertext) if c.note_ciphertext else None
            halt_dto = HALTFlags(
                hungry=c.halt_hungry,
                angry=c.halt_angry,
                lonely=c.halt_lonely,
                tired=c.halt_tired,
            )
            result.append(
                CheckInResponse(
                    id=c.id,
                    mood=c.mood,
                    sleep_quality=c.sleep_quality,
                    craving=c.craving,
                    halt=halt_dto,
                    note=decrypted_note,
                    source=c.source,
                    created_at=c.created_at,
                )
            )
        return result
