"""
Anchor — Urge Surfing / Interventions API Router.

POST /interventions/urge-surf/start        — Start 4-minute timed urge surfing wave session.
POST /interventions/urge-surf/{id}/complete — Complete session and record craving delta.
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.urge import (
    UrgeSurfCompleteRequest,
    UrgeSurfCompleteResponse,
    UrgeSurfStartRequest,
    UrgeSurfStartResponse,
)
from app.services.urge_service import UrgeService

router = APIRouter()


@router.post("/urge-surf/start", status_code=status.HTTP_201_CREATED, response_model=UrgeSurfStartResponse)
async def start_urge_surf(
    req: UrgeSurfStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start 4-minute guided wave breathing urge surfing intervention."""
    service = UrgeService(db)
    return await service.start_urge_surf(current_user.id, req)


@router.post("/urge-surf/{intervention_id}/complete", response_model=UrgeSurfCompleteResponse)
async def complete_urge_surf(
    intervention_id: uuid.UUID,
    req: UrgeSurfCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Complete urge surfing session and record craving delta."""
    service = UrgeService(db)
    return await service.complete_urge_surf(current_user.id, intervention_id, req)
