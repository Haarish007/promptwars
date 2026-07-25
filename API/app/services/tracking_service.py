"""
Anchor — Tracking & Milestones Service.

Manages:
  - Recovery milestone days calculation
  - Compassionate reset flow (reframes setbacks as data points without shame per docs/08 §1.1)
  - Medication scheduling & compliance logging
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tracking import Medication, MedicationLog, Milestone
from app.repositories.user_repo import UserRepository
from app.schemas.tracking import (
    MedicationCreateRequest,
    MedicationLogRequest,
    MedicationLogResponse,
    MedicationResponse,
    MilestoneResponse,
    ResetMilestoneRequest,
    ResetMilestoneResponse,
)

COMPASSIONATE_RESET_MESSAGE = (
    "Recovery is a journey with twists, not a straight line. Every day of effort you've built "
    "remains a permanent part of your strength. Today is simply a data point to learn from, "
    "not a restart from zero. We are right here with you."
)


class TrackingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def get_milestone(self, user_id: uuid.UUID) -> MilestoneResponse:
        """Calculate active recovery days accumulated by member."""
        stmt = (
            select(Milestone)
            .where(Milestone.user_id == user_id)
            .order_by(Milestone.created_at.desc())
            .limit(1)
        )
        res = await self.session.execute(stmt)
        milestone = res.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if not milestone:
            # Fallback to profile start date
            profile = await self.user_repo.get_profile(user_id)
            start_dt = (
                datetime.combine(profile.recovery_start_date, datetime.min.time(), tzinfo=timezone.utc)
                if profile and profile.recovery_start_date
                else now
            )
            days_count = max(0, (now - start_dt).days)
            return MilestoneResponse(
                id=None,
                kind="streak",
                days_count=days_count,
                achieved_at=start_dt,
                reset_at=None,
                note=None,
            )

        # Days count since achieved_at or reset_at
        base_time = milestone.reset_at or milestone.achieved_at
        days_count = max(0, (now - base_time).days)

        return MilestoneResponse(
            id=milestone.id,
            kind=milestone.kind,
            days_count=days_count,
            achieved_at=milestone.achieved_at,
            reset_at=milestone.reset_at,
            note=milestone.note,
        )

    async def reset_milestone(
        self, user_id: uuid.UUID, req: ResetMilestoneRequest
    ) -> ResetMilestoneResponse:
        """
        Compassionate reset flow.
        Frames setback as a data point in a long journey, preserving past effort.
        """
        now = datetime.now(timezone.utc)
        milestone = Milestone(
            user_id=user_id,
            kind="setback_reset",
            achieved_at=now,
            reset_at=now,
            note=req.note,
        )
        self.session.add(milestone)
        await self.session.flush()

        milestone_dto = MilestoneResponse(
            id=milestone.id,
            kind=milestone.kind,
            days_count=0,
            achieved_at=now,
            reset_at=now,
            note=req.note,
        )

        suggested_action = {
            "type": "urge_surf",
            "label": "Take a 4-minute Urge Surf or Grounding reset right now",
        }

        return ResetMilestoneResponse(
            milestone=milestone_dto,
            compassionate_message=COMPASSIONATE_RESET_MESSAGE,
            suggested_action=suggested_action,
        )

    async def add_medication(
        self, user_id: uuid.UUID, req: MedicationCreateRequest
    ) -> MedicationResponse:
        med = Medication(
            user_id=user_id,
            name=req.name,
            schedule=req.schedule,
            active=True,
        )
        self.session.add(med)
        await self.session.flush()
        return MedicationResponse.model_validate(med)

    async def get_medications(self, user_id: uuid.UUID) -> List[MedicationResponse]:
        stmt = select(Medication).where(Medication.user_id == user_id, Medication.active.is_(True))
        res = await self.session.execute(stmt)
        meds = res.scalars().all()
        return [MedicationResponse.model_validate(m) for m in meds]

    async def log_medication(
        self, user_id: uuid.UUID, medication_id: uuid.UUID, req: MedicationLogRequest
    ) -> MedicationLogResponse:
        now = datetime.now(timezone.utc)
        log = MedicationLog(
            medication_id=medication_id,
            taken_at=now,
            status=req.status,
        )
        self.session.add(log)
        await self.session.flush()
        return MedicationLogResponse.model_validate(log)
