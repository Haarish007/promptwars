"""
Anchor — Notification & Nudges Service.

Enforces:
  - Quiet hours compliance (e.g., 22:00-07:00 in member profile)
  - Daily nudge cap (nudge_max_per_day = 3)
"""

from __future__ import annotations

import uuid
from datetime import datetime, time as dtime, timezone
from typing import List
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.notification import Notification
from app.repositories.user_repo import UserRepository
from app.schemas.notification import NotificationResponse, NotificationScheduleRequest


def is_within_quiet_hours(
    target_dt: datetime, quiet_start_str: str = "22:00", quiet_end_str: str = "07:00"
) -> bool:
    """Check if target_dt falls within quiet hours range (e.g., 22:00 to 07:00)."""
    try:
        sh, sm = map(int, quiet_start_str.split(":"))
        eh, em = map(int, quiet_end_str.split(":"))
        start_time = dtime(sh, sm)
        end_time = dtime(eh, em)

        t = target_dt.time()
        if start_time > end_time:
            # Overnight range (e.g. 22:00 to 07:00)
            return t >= start_time or t < end_time
        return start_time <= t < end_time
    except Exception:
        return False


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def schedule_notification(
        self, user_id: uuid.UUID, req: NotificationScheduleRequest
    ) -> NotificationResponse:
        profile = await self.user_repo.get_profile(user_id)
        quiet_start = profile.quiet_hours_start if profile else "22:00"
        quiet_end = profile.quiet_hours_end if profile else "07:00"

        # Check quiet hours compliance
        if is_within_quiet_hours(req.scheduled_for, quiet_start, quiet_end):
            # Suppress/skip notification scheduled during quiet hours
            notification = Notification(
                user_id=user_id,
                type=req.type,
                scheduled_for=req.scheduled_for,
                sent_at=None,
                payload=req.payload,
                status="skipped",
            )
            self.session.add(notification)
            await self.session.flush()
            return NotificationResponse.model_validate(notification)

        # Check daily nudge cap (nudge_max_per_day = 3)
        if req.type == "nudge":
            start_of_day = req.scheduled_for.replace(hour=0, minute=0, second=0, microsecond=0)
            stmt = select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.type == "nudge",
                Notification.scheduled_for >= start_of_day,
                Notification.status != "skipped",
            )
            res = await self.session.execute(stmt)
            count = res.scalar() or 0

            max_cap = settings.nudge_max_per_day
            if count >= max_cap:
                notification = Notification(
                    user_id=user_id,
                    type=req.type,
                    scheduled_for=req.scheduled_for,
                    sent_at=None,
                    payload=req.payload,
                    status="skipped",
                )
                self.session.add(notification)
                await self.session.flush()
                return NotificationResponse.model_validate(notification)

        # Schedule active notification
        notification = Notification(
            user_id=user_id,
            type=req.type,
            scheduled_for=req.scheduled_for,
            sent_at=None,
            payload=req.payload,
            status="pending",
        )
        self.session.add(notification)
        await self.session.flush()
        return NotificationResponse.model_validate(notification)

    async def get_user_notifications(
        self, user_id: uuid.UUID, limit: int = 20
    ) -> List[NotificationResponse]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.scheduled_for.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        notes = res.scalars().all()
        return [NotificationResponse.model_validate(n) for n in notes]
