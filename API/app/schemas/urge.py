"""
Anchor — Urge Surfing Intervention Schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class UrgeSurfStartRequest(BaseModel):
    craving_before: int = Field(ge=0, le=10, description="0 (none) to 10 (intense)")


class UrgeSurfStartResponse(BaseModel):
    intervention_id: uuid.UUID
    duration_seconds: int = 240  # 4 minutes
    guidance_steps: List[str]
    started_at: datetime


class UrgeSurfCompleteRequest(BaseModel):
    craving_after: int = Field(ge=0, le=10, description="0 (none) to 10 (intense)")
    outcome: str = Field(default="completed", pattern="^(completed|abandoned)$")


class UrgeSurfCompleteResponse(BaseModel):
    intervention_id: uuid.UUID
    craving_before: int
    craving_after: int
    craving_delta: int
    outcome: str
    message: str
