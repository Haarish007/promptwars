"""
Anchor — Safety Event & Audit Log Repository.
"""

from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.safety import SafetyEvent
from app.models.audit import AuditLog


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def log_safety_event(self, event: SafetyEvent) -> SafetyEvent:
        self.session.add(event)
        await self.session.flush()
        return event

    async def log_audit_event(self, log: AuditLog) -> AuditLog:
        self.session.add(log)
        await self.session.flush()
        return log

    async def get_safety_events_for_user(self, user_id) -> Sequence[SafetyEvent]:
        stmt = (
            select(SafetyEvent)
            .where(SafetyEvent.user_id == user_id)
            .order_by(SafetyEvent.created_at.desc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
