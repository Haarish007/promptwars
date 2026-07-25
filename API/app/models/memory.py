"""
Anchor — Memory Event ORM Model (Per-user RAG).
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class MemoryEvent(Base, TimestampMixin):
    __tablename__ = "memory_events"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(50), nullable=False)  # trigger | worked_intervention | milestone | preference | relationship
    content: Mapped[str] = mapped_column(Text, nullable=False)
    salience: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    source_ref: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
