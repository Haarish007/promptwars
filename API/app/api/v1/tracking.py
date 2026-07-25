"""
Anchor — Tracking & Milestones API Router.

GET  /tracking/milestones          — Get recovery milestone days count
POST /tracking/milestones/reset    — Compassionate reset flow
GET  /tracking/medications         — Get active medications list
POST /tracking/medications         — Add medication schedule
POST /tracking/medications/{id}/log — Log medication compliance (taken/missed/skipped)
"""

from __future__ import annotations

import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.tracking import (
    MedicationCreateRequest,
    MedicationLogRequest,
    MedicationLogResponse,
    MedicationResponse,
    MilestoneResponse,
    ResetMilestoneRequest,
    ResetMilestoneResponse,
)
from app.services.tracking_service import TrackingService

router = APIRouter()


@router.get("/milestones", response_model=MilestoneResponse)
async def get_milestone(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get active recovery days milestone count."""
    service = TrackingService(db)
    return await service.get_milestone(current_user.id)


@router.post("/milestones/reset", response_model=ResetMilestoneResponse)
async def reset_milestone(
    req: ResetMilestoneRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Compassionate milestone reset flow (frames setback as a data point without shame)."""
    service = TrackingService(db)
    return await service.reset_milestone(current_user.id, req)


@router.get("/medications", response_model=List[MedicationResponse])
async def get_medications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of active medication schedules."""
    service = TrackingService(db)
    return await service.get_medications(current_user.id)


@router.post("/medications", status_code=status.HTTP_201_CREATED, response_model=MedicationResponse)
async def add_medication(
    req: MedicationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add new medication schedule."""
    service = TrackingService(db)
    return await service.add_medication(current_user.id, req)


@router.post("/medications/{medication_id}/log", response_model=MedicationLogResponse)
async def log_medication(
    medication_id: uuid.UUID,
    req: MedicationLogRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Log medication status (taken/missed/skipped)."""
    service = TrackingService(db)
    return await service.log_medication(current_user.id, medication_id, req)
