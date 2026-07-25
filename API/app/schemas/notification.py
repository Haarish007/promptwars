"""
Anchor — Notification Schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class NotificationScheduleRequest(BaseModel):
    type: str = Field(pattern="^(nudge|reminder|share_alert)$")
    scheduled_for: datetime
    payload: Dict[str, Any] = Field(default_factory=dict)


class NotificationResponse(BaseModel):
    id: uuid.UUID
    type: str
    scheduled_for: datetime
    sent_at: Optional[datetime] = None
    payload: Dict[str, Any]
    status: str = Field(pattern="^(pending|sent|acknowledged|skipped)$")
    created_at: datetime

    model_config = {"from_attributes": True}
