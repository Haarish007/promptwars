"""
Anchor — Check-in ORM Model.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class CheckIn(Base, TimestampMixin):
    __tablename__ = "check_ins"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    mood: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    sleep_quality: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    craving: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    halt_hungry: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    halt_angry: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    halt_lonely: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    halt_tired: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    note_ciphertext: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    source: Mapped[str] = mapped_column(String(20), default="tap", nullable=False)  # tap | voice

    __table_args__ = (
        CheckConstraint("mood >= 1 AND mood <= 5", name="chk_checkin_mood_range"),
        CheckConstraint("sleep_quality >= 1 AND sleep_quality <= 5", name="chk_checkin_sleep_range"),
        CheckConstraint("craving >= 0 AND craving <= 10", name="chk_checkin_craving_range"),
        Index("ix_checkins_user_created", "user_id", "created_at"),
    )
