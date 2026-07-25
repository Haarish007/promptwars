"""
Anchor — Knowledge Base Repository.
"""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kb import KBArticle, KBChunk


class KBRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_article(self, article: KBArticle) -> KBArticle:
        self.session.add(article)
        await self.session.flush()
        return article

    async def add_chunk(self, chunk: KBChunk) -> KBChunk:
        self.session.add(chunk)
        await self.session.flush()
        return chunk

    async def get_all_articles(self) -> Sequence[KBArticle]:
        stmt = select(KBArticle).order_by(KBArticle.title)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_article_by_id(self, article_id: uuid.UUID) -> KBArticle | None:
        stmt = select(KBArticle).where(KBArticle.id == article_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def search_chunks(self, query_text: str, limit: int = 4) -> Sequence[KBChunk]:
        # Keyword search for the build per NFR-MNT / config
        stmt = (
            select(KBChunk)
            .where(KBChunk.chunk_text.ilike(f"%{query_text}%"))
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
