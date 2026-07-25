"""
Anchor — Caregiver Circle & Copilot Schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class CaregiverInviteRequest(BaseModel):
    guardian_email: EmailStr


class CaregiverLinkResponse(BaseModel):
    id: uuid.UUID
    member_id: uuid.UUID
    guardian_id: uuid.UUID
    status: str = Field(pattern="^(invited|active|revoked)$")
    invited_at: datetime
    accepted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ShareProposeRequest(BaseModel):
    kind: str = Field(pattern="^(hard_moment|milestone|checkin_summary)$")
    summary: str = Field(min_length=1, max_length=2000)


class CaregiverSuggestionDTO(BaseModel):
    suggested_message: str
    avoid: List[str] = Field(default_factory=list)
    rationale: str


class ShareEventResponse(BaseModel):
    id: uuid.UUID
    member_id: uuid.UUID
    guardian_id: uuid.UUID
    kind: str
    summary: str
    suggestion: Optional[CaregiverSuggestionDTO] = None
    created_at: datetime

    model_config = {"from_attributes": True}
