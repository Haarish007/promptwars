"""
Anchor — Caregiver Repository.
"""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.caregiver import CaregiverLink, ShareEvent, CaregiverSuggestion


class CaregiverRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_link(self, link: CaregiverLink) -> CaregiverLink:
        self.session.add(link)
        await self.session.flush()
        return link

    async def get_link_by_id(self, link_id: uuid.UUID) -> CaregiverLink | None:
        stmt = select(CaregiverLink).where(CaregiverLink.id == link_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_active_link_for_member(self, member_id: uuid.UUID) -> CaregiverLink | None:
        stmt = select(CaregiverLink).where(
            CaregiverLink.member_id == member_id,
            CaregiverLink.status == "active"
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_share_event(self, event: ShareEvent) -> ShareEvent:
        self.session.add(event)
        await self.session.flush()
        return event

    async def save_suggestion(self, suggestion: CaregiverSuggestion) -> CaregiverSuggestion:
        self.session.add(suggestion)
        await self.session.flush()
        return suggestion

    async def get_guardian_feed(self, guardian_id: uuid.UUID, limit: int = 20) -> Sequence[ShareEvent]:
        stmt = (
            select(ShareEvent)
            .where(ShareEvent.guardian_id == guardian_id)
            .order_by(ShareEvent.created_at.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
