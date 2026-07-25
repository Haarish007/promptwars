"""
Anchor — Check-in Schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class HALTFlags(BaseModel):
    hungry: bool = False
    angry: bool = False
    lonely: bool = False
    tired: bool = False


class CheckInSubmitRequest(BaseModel):
    mood: int = Field(ge=1, le=5, description="1 (very poor) to 5 (excellent)")
    sleep_quality: int = Field(ge=1, le=5, description="1 (very poor) to 5 (excellent)")
    craving: int = Field(ge=0, le=10, description="0 (none) to 10 (intense)")
    halt: HALTFlags = Field(default_factory=HALTFlags)
    note: Optional[str] = Field(default=None, max_length=2000)
    source: str = Field(default="tap", pattern="^(tap|voice)$")


class CheckInResponse(BaseModel):
    id: uuid.UUID
    mood: int
    sleep_quality: int
    craving: int
    halt: HALTFlags
    note: Optional[str] = None
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SuggestedActionDTO(BaseModel):
    type: str  # grounding | urge_surf | halt_reset | connect
    label: str


class CheckInSubmitResponse(BaseModel):
    checkin: CheckInResponse
    risk: dict  # RiskScoreResponse dictionary
    suggested_action: SuggestedActionDTO
