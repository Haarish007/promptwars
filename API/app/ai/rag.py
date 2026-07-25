"""
Anchor — RAG Context Assembly Module.

Retrieves:
  1. Top-k curated KB passages ([kb-101], [kb-102], [kb-103]) matching user query
  2. User Recovery Memory events (triggers, past effective interventions, milestones)
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.kb_repo import KBRepository
from app.repositories.memory_repo import MemoryRepository


class RAGRetriever:
    """Retrieves grounded KB chunks and personalized user memory events."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.kb_repo = KBRepository(session)
        self.memory_repo = MemoryRepository(session)

    async def retrieve_kb_chunks(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Search Knowledge Base chunks matching query.
        Returns passage items with id, chunk_text, and article title.
        """
        chunks = await self.kb_repo.search_chunks(query, limit=top_k)
        if not chunks:
            # Fallback: get all article chunks if keyword query yielded empty
            articles = await self.kb_repo.get_all_articles()
            result = []
            for art in articles[:top_k]:
                for chk in art.chunks[:1]:
                    result.append({
                        "id": f"kb-{chk.id.hex[:4]}",
                        "title": art.title,
                        "text": chk.chunk_text,
                    })
            return result

        result = []
        for chk in chunks:
            result.append({
                "id": f"kb-{chk.id.hex[:4]}",
                "title": chk.article.title if chk.article else "Recovery Guidance",
                "text": chk.chunk_text,
            })
        return result

    async def retrieve_user_memory(self, user_id: uuid.UUID, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve active user recovery memory events."""
        events = await self.memory_repo.get_user_events(user_id, limit=top_k)
        result = []
        for evt in events:
            result.append({
                "kind": evt.kind,
                "content": evt.content,
                "salience": evt.salience,
            })
        return result
