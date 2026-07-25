"""
Anchor — Notifications & Nudges API Router.

GET  /notifications — List notifications history
POST /notifications — Schedule notification nudge (respecting quiet hours and daily max cap)
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.notification import NotificationResponse, NotificationScheduleRequest
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get notifications history."""
    service = NotificationService(db)
    return await service.get_user_notifications(current_user.id)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=NotificationResponse)
async def schedule_notification(
    req: NotificationScheduleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Schedule notification nudge.
    Automatically checks quiet hours compliance (22:00-07:00) and daily max cap (3 nudges/day).
    """
    service = NotificationService(db)
    return await service.schedule_notification(current_user.id, req)
