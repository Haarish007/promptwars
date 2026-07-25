"""
Anchor — Consent API Router.

POST   /consents          — Grant explicit consent
DELETE /consents/{scope}  — Revoke consent (immediate)
GET    /consents          — List active consent scopes
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.consent import ConsentGrantRequest, ConsentResponse
from app.services.consent_service import ConsentService

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ConsentResponse)
async def grant_consent(
    req: ConsentGrantRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Grant versioned, scoped consent."""
    service = ConsentService(db)
    return await service.grant_consent(current_user.id, req)


@router.delete("/{scope}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_consent(
    scope: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke consent for a specific scope (immediate enforcement)."""
    service = ConsentService(db)
    await service.revoke_consent(current_user.id, scope)
    return None


@router.get("", response_model=List[ConsentResponse])
async def list_consents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all active consents for current user."""
    service = ConsentService(db)
    return await service.list_consents(current_user.id)
