"""
Anchor — Onboarding & Profile Schemas.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field


class EmergencyContactRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    relationship: str = Field(min_length=1, max_length=50)
    phone: str = Field(min_length=5, max_length=20)
    is_sponsor: bool = Field(default=False)
    priority: int = Field(default=1, ge=1)


class EmergencyContactResponse(BaseModel):
    id: uuid.UUID
    name: str
    relationship: str
    phone: str
    is_sponsor: bool
    priority: int

    model_config = {"from_attributes": True}


class TriggerRequest(BaseModel):
    label: str = Field(min_length=1, max_length=100)
    type: str = Field(pattern="^(emotional|environmental|social|temporal)$")
    time_of_day: Optional[str] = None
    location_context: Optional[str] = None


class TriggerResponse(BaseModel):
    id: uuid.UUID
    label: str
    type: str
    time_of_day: Optional[str] = None
    location_context: Optional[str] = None

    model_config = {"from_attributes": True}


class ProfileResponse(BaseModel):
    user_id: uuid.UUID
    recovery_goal: Optional[str] = None
    substance_focus: Optional[str] = None
    recovery_start_date: Optional[date] = None
    voice_first: bool = False
    nudge_frequency: str = "medium"
    quiet_hours_start: Optional[str] = "22:00"
    quiet_hours_end: Optional[str] = "07:00"
    region: str = "US"

    model_config = {"from_attributes": True}


class ProfileUpdateRequest(BaseModel):
    recovery_goal: Optional[str] = None
    substance_focus: Optional[str] = None
    recovery_start_date: Optional[date] = None
    voice_first: Optional[bool] = None
    nudge_frequency: Optional[str] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    region: Optional[str] = None


class OnboardingSubmitRequest(BaseModel):
    recovery_goal: Optional[str] = None
    substance_focus: Optional[str] = None
    recovery_start_date: Optional[date] = None
    region: str = Field(default="US")
    voice_first: bool = Field(default=False)
    quiet_hours_start: Optional[str] = "22:00"
    quiet_hours_end: Optional[str] = "07:00"
    triggers: List[TriggerRequest] = Field(default_factory=list)
    emergency_contact: Optional[EmergencyContactRequest] = None
