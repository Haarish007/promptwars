"""
Anchor — Memory Repository.
"""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import MemoryEvent


class MemoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_event(self, event: MemoryEvent) -> MemoryEvent:
        self.session.add(event)
        await self.session.flush()
        return event

    async def get_user_events(self, user_id: uuid.UUID, limit: int = 20) -> Sequence[MemoryEvent]:
        stmt = (
            select(MemoryEvent)
            .where(MemoryEvent.user_id == user_id)
            .order_by(MemoryEvent.created_at.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
