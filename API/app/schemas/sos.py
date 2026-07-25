"""
Anchor — SOS Crisis Flow Schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class OneTapActionDTO(BaseModel):
    id: str
    label: str
    action_type: str = Field(pattern="^(call|sms|urge_surf|link)$")
    target: str


class SOSRequest(BaseModel):
    region: Optional[str] = Field(default=None, description="Region code e.g. US, IN")
    voice_triggered: bool = Field(default=False)


class SOSResponse(BaseModel):
    response_text: str
    crisis_line: dict
    emergency_contacts: List[dict] = Field(default_factory=list)
    one_tap_actions: List[OneTapActionDTO] = Field(default_factory=list)
    timestamp: datetime
