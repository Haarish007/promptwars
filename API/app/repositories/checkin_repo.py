"""
Anchor — Check-in Repository.
"""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checkin import CheckIn


class CheckInRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, checkin: CheckIn) -> CheckIn:
        self.session.add(checkin)
        await self.session.flush()
        return checkin

    async def get_by_id(self, checkin_id: uuid.UUID) -> CheckIn | None:
        stmt = select(CheckIn).where(CheckIn.id == checkin_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_user_history(self, user_id: uuid.UUID, limit: int = 30) -> Sequence[CheckIn]:
        stmt = (
            select(CheckIn)
            .where(CheckIn.user_id == user_id)
            .order_by(CheckIn.created_at.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
