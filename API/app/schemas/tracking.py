"""
Anchor — Tracking & Milestone Schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MilestoneResponse(BaseModel):
    id: Optional[uuid.UUID] = None
    kind: str
    days_count: int
    achieved_at: datetime
    reset_at: Optional[datetime] = None
    note: Optional[str] = None

    model_config = {"from_attributes": True}


class ResetMilestoneRequest(BaseModel):
    note: Optional[str] = Field(default=None, max_length=1000)


class ResetMilestoneResponse(BaseModel):
    milestone: MilestoneResponse
    compassionate_message: str
    suggested_action: dict


class MedicationCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    schedule: Dict[str, Any] = Field(default_factory=dict)


class MedicationResponse(BaseModel):
    id: uuid.UUID
    name: str
    schedule: Dict[str, Any]
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MedicationLogRequest(BaseModel):
    status: str = Field(pattern="^(taken|missed|skipped)$")


class MedicationLogResponse(BaseModel):
    id: uuid.UUID
    medication_id: uuid.UUID
    status: str
    taken_at: datetime

    model_config = {"from_attributes": True}
