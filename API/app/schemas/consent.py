"""
Anchor — Consent Schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ConsentGrantRequest(BaseModel):
    scope: str = Field(pattern="^(data_processing|share_with_guardian|voice_processing)$")
    version: str = Field(default="1.0")


class ConsentResponse(BaseModel):
    id: uuid.UUID
    scope: str
    version: str
    granted_at: datetime
    revoked_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
