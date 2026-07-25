"""
Anchor — Consent Repository.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.consent import Consent


class ConsentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def grant_consent(self, consent: Consent) -> Consent:
        self.session.add(consent)
        await self.session.flush()
        return consent

    async def get_active_consents(self, user_id: uuid.UUID) -> Sequence[Consent]:
        stmt = select(Consent).where(
            Consent.user_id == user_id,
            Consent.revoked_at.is_(None)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def has_active_consent(self, user_id: uuid.UUID, scope: str) -> bool:
        stmt = select(Consent).where(
            Consent.user_id == user_id,
            Consent.scope == scope,
            Consent.revoked_at.is_(None)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none() is not None

    async def revoke_consent(self, user_id: uuid.UUID, scope: str) -> bool:
        stmt = select(Consent).where(
            Consent.user_id == user_id,
            Consent.scope == scope,
            Consent.revoked_at.is_(None)
        )
        res = await self.session.execute(stmt)
        consents = res.scalars().all()
        now = datetime.now(timezone.utc)
        for c in consents:
            c.revoked_at = now
        await self.session.flush()
        return len(consents) > 0
