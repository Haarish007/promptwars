"""
Anchor — Urge Surfing Intervention Service.

Manages 4-minute timed wave breathing state machine:
  - Initializes intervention record in interventions table
  - Tracks craving before (0-10) and craving after (0-10)
  - Computes craving delta (reduction)
  - Saves positive Recovery Memory event if craving decreased
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.intervention import Intervention
from app.models.memory import MemoryEvent
from app.repositories.memory_repo import MemoryRepository
from app.schemas.urge import (
    UrgeSurfCompleteRequest,
    UrgeSurfCompleteResponse,
    UrgeSurfStartRequest,
    UrgeSurfStartResponse,
)

WAVE_GUIDANCE_STEPS = [
    "Step 1: Notice where in your body you feel the craving. Acknowledge it without judgment.",
    "Step 2: Picture the craving as an ocean wave rising up. You are the surfer riding on top.",
    "Step 3: Breathe steadily into the wave — inhale for 4 seconds, exhale for 6 seconds.",
    "Step 4: Watch the wave reach its peak and naturally subside as peace returns.",
]


class UrgeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.memory_repo = MemoryRepository(session)

    async def start_urge_surf(
        self, user_id: uuid.UUID, req: UrgeSurfStartRequest
    ) -> UrgeSurfStartResponse:
        now = datetime.now(timezone.utc)
        intervention = Intervention(
            user_id=user_id,
            type="urge_surf",
            started_at=now,
            craving_before=req.craving_before,
            outcome="in_progress",
        )
        self.session.add(intervention)
        await self.session.flush()

        return UrgeSurfStartResponse(
            intervention_id=intervention.id,
            duration_seconds=240,  # 4 minutes
            guidance_steps=WAVE_GUIDANCE_STEPS,
            started_at=now,
        )

    async def complete_urge_surf(
        self, user_id: uuid.UUID, intervention_id: uuid.UUID, req: UrgeSurfCompleteRequest
    ) -> UrgeSurfCompleteResponse:
        stmt = select(Intervention).where(
            Intervention.id == intervention_id,
            Intervention.user_id == user_id,
        )
        res = await self.session.execute(stmt)
        intervention = res.scalar_one_or_none()

        if not intervention:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Intervention record not found",
            )

        now = datetime.now(timezone.utc)
        intervention.completed_at = now
        intervention.craving_after = req.craving_after
        intervention.outcome = req.outcome

        craving_before = intervention.craving_before or 0
        craving_delta = craving_before - req.craving_after

        message = "Urge surfing session completed."
        if req.outcome == "completed" and craving_delta > 0:
            message = f"Great work! Your craving dropped by {craving_delta} points."
            # Save positive Recovery Memory event
            mem_event = MemoryEvent(
                user_id=user_id,
                kind="worked_intervention",
                content=f"Urge surfing reduced craving from {craving_before} to {req.craving_after} (delta -{craving_delta})",
                salience=1.2,
                source_ref=f"intervention:{intervention.id}",
            )
            await self.memory_repo.add_event(mem_event)

        return UrgeSurfCompleteResponse(
            intervention_id=intervention.id,
            craving_before=craving_before,
            craving_after=req.craving_after,
            craving_delta=craving_delta,
            outcome=req.outcome,
            message=message,
        )
