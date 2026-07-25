"""
Anchor — Onboarding & Profile API Router.

POST   /onboarding          — Submit onboarding (<90s path)
GET    /profile             — Read current user profile
PUT    /profile             — Update profile
GET    /emergency-contacts  — Get emergency contacts
POST   /emergency-contacts  — Add emergency contact
GET    /triggers            — List triggers
POST   /triggers            — Add trigger
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.onboarding import (
    EmergencyContactRequest,
    EmergencyContactResponse,
    OnboardingSubmitRequest,
    ProfileResponse,
    ProfileUpdateRequest,
    TriggerRequest,
    TriggerResponse,
)
from app.services.onboarding_service import OnboardingService

router = APIRouter()


@router.post("/onboarding", status_code=status.HTTP_201_CREATED, response_model=ProfileResponse)
async def submit_onboarding(
    req: OnboardingSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit onboarding data (<90 seconds setup)."""
    service = OnboardingService(db)
    return await service.submit_onboarding(current_user.id, req)


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current member profile."""
    service = OnboardingService(db)
    return await service.get_profile(current_user.id)


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    req: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update profile parameters."""
    service = OnboardingService(db)
    return await service.update_profile(current_user.id, req)


@router.get("/emergency-contacts", response_model=List[EmergencyContactResponse])
async def get_emergency_contacts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get emergency contacts (phones decrypted for authorized owner)."""
    service = OnboardingService(db)
    return await service.get_emergency_contacts(current_user.id)


@router.post("/emergency-contacts", status_code=status.HTTP_201_CREATED, response_model=EmergencyContactResponse)
async def add_emergency_contact(
    req: EmergencyContactRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add emergency contact (phone encrypted at rest)."""
    service = OnboardingService(db)
    return await service.add_emergency_contact(current_user.id, req)


@router.get("/triggers", response_model=List[TriggerResponse])
async def get_triggers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List known triggers for current user."""
    # Stub for listing triggers
    return []


@router.post("/triggers", status_code=status.HTTP_201_CREATED, response_model=TriggerResponse)
async def add_trigger(
    req: TriggerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a known trigger."""
    service = OnboardingService(db)
    return await service.add_trigger(current_user.id, req)
