"""
Anchor — Risk Score Schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class FactorDTO(BaseModel):
    factor: str
    impact: str
    detail: str


class RiskScoreResponse(BaseModel):
    id: Optional[uuid.UUID] = None
    score: int = Field(ge=0, le=100)
    band: str = Field(pattern="^(low|guarded|elevated|high)$")
    factors: List[FactorDTO] = Field(default_factory=list)
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
