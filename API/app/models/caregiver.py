"""
Anchor — Caregiver ORM Models.
Includes unique-active-caregiver-link constraint.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class CaregiverLink(Base, TimestampMixin):
    __tablename__ = "caregiver_links"

    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    guardian_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="invited", nullable=False)  # invited | active | revoked
    invited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now(), nullable=False)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index(
            "uq_active_caregiver_link",
            "member_id",
            unique=True,
            postgresql_where=(status == "active"),
        ),
    )


class ShareEvent(Base, TimestampMixin):
    __tablename__ = "share_events"

    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    guardian_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(50), nullable=False)  # hard_moment | milestone | checkin_summary
    summary_ciphertext: Mapped[str] = mapped_column(String(2048), nullable=False)

    suggestion: Mapped[Optional[CaregiverSuggestion]] = relationship("CaregiverSuggestion", back_populates="share_event", uselist=False, cascade="all, delete-orphan")


class CaregiverSuggestion(Base, TimestampMixin):
    __tablename__ = "caregiver_suggestions"

    share_event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("share_events.id", ondelete="CASCADE"), unique=True, nullable=False)
    suggested_message: Mapped[str] = mapped_column(String(1000), nullable=False)
    avoid: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    rationale: Mapped[str] = mapped_column(String(1000), nullable=False)

    share_event: Mapped[ShareEvent] = relationship("ShareEvent", back_populates="suggestion")
