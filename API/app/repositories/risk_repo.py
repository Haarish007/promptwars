"""
Anchor — Risk Score & Risk Config Repository.
"""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.risk import RiskScore, RiskConfig


class RiskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_score(self, score: RiskScore) -> RiskScore:
        self.session.add(score)
        await self.session.flush()
        return score

    async def get_latest_score(self, user_id: uuid.UUID) -> RiskScore | None:
        stmt = (
            select(RiskScore)
            .where(RiskScore.user_id == user_id)
            .order_by(RiskScore.created_at.desc())
            .limit(1)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_score_history(self, user_id: uuid.UUID, limit: int = 30) -> Sequence[RiskScore]:
        stmt = (
            select(RiskScore)
            .where(RiskScore.user_id == user_id)
            .order_by(RiskScore.created_at.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_active_config(self, key: str = "default") -> RiskConfig | None:
        stmt = select(RiskConfig).where(RiskConfig.key == key, RiskConfig.active.is_(True))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def save_config(self, config: RiskConfig) -> RiskConfig:
        self.session.add(config)
        await self.session.flush()
        return config
