"""
Anchor — Caregiver & Copilot API Router.

POST   /caregiver/invite        — Member invites guardian by email
POST   /caregiver/accept/{id}   — Guardian accepts invitation
DELETE /caregiver/link          — Revoke caregiver link
POST   /caregiver/share         — Propose sharing moment (requires active link & consent)
GET    /caregiver/feed          — Guardian feed with Copilot guidance
"""

from __future__ import annotations

import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.caregiver import (
    CaregiverInviteRequest,
    CaregiverLinkResponse,
    ShareEventResponse,
    ShareProposeRequest,
)
from app.services.caregiver_service import CaregiverService

router = APIRouter()


@router.post("/invite", status_code=status.HTTP_201_CREATED, response_model=CaregiverLinkResponse)
async def invite_caregiver(
    req: CaregiverInviteRequest,
    current_user: User = Depends(require_role("member")),
    db: AsyncSession = Depends(get_db),
):
    """Member invites guardian by email."""
    service = CaregiverService(db)
    return await service.invite_caregiver(current_user.id, req)


@router.post("/accept/{link_id}", response_model=CaregiverLinkResponse)
async def accept_invite(
    link_id: uuid.UUID,
    current_user: User = Depends(require_role("guardian")),
    db: AsyncSession = Depends(get_db),
):
    """Guardian accepts link invitation."""
    service = CaregiverService(db)
    return await service.accept_invite(current_user.id, link_id)


@router.delete("/link", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_link(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke active caregiver link."""
    service = CaregiverService(db)
    await service.revoke_link(current_user.id)
    return None


@router.post("/share", status_code=status.HTTP_201_CREATED, response_model=ShareEventResponse)
async def propose_share(
    req: ShareProposeRequest,
    current_user: User = Depends(require_role("member")),
    db: AsyncSession = Depends(get_db),
):
    """
    Member explicitly proposes sharing a moment summary.
    Enforces active caregiver link AND active share_with_guardian consent (TC-CAR-004).
    Returns Copilot 3-element guidance.
    """
    service = CaregiverService(db)
    return await service.propose_share(current_user.id, req)


@router.get("/feed", response_model=List[ShareEventResponse])
async def get_guardian_feed(
    current_user: User = Depends(require_role("guardian")),
    db: AsyncSession = Depends(get_db),
):
    """Guardian feed containing member share events and Copilot guidance."""
    service = CaregiverService(db)
    return await service.get_guardian_feed(current_user.id)
