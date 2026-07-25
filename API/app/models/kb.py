"""
Anchor — Knowledge Base ORM Models.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any, Optional

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class KBArticle(Base, TimestampMixin):
    __tablename__ = "kb_articles"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    review_date: Mapped[date] = mapped_column(Date, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)

    chunks: Mapped[list[KBChunk]] = relationship("KBChunk", back_populates="article", cascade="all, delete-orphan")


class KBChunk(Base, TimestampMixin):
    __tablename__ = "kb_chunks"

    article_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("kb_articles.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    ord: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    article: Mapped[KBArticle] = relationship("KBArticle", back_populates="chunks")
