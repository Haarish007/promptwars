"""
Anchor — Profile, Emergency Contact, and Trigger ORM Models.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class MemberProfile(Base, TimestampMixin):
    __tablename__ = "member_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    recovery_goal: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    substance_focus: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    recovery_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    voice_first: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    nudge_frequency: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    quiet_hours_start: Mapped[Optional[str]] = mapped_column(String(5), nullable=True, default="22:00")  # HH:MM
    quiet_hours_end: Mapped[Optional[str]] = mapped_column(String(5), nullable=True, default="07:00")    # HH:MM
    region: Mapped[str] = mapped_column(String(10), default="US", nullable=False)

    user: Mapped[User] = relationship("User", back_populates="profile")


class EmergencyContact(Base, TimestampMixin):
    __tablename__ = "emergency_contacts"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    relationship: Mapped[str] = mapped_column(String(50), nullable=False)
    phone_ciphertext: Mapped[str] = mapped_column(String(512), nullable=False)
    is_sponsor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class Trigger(Base, TimestampMixin):
    __tablename__ = "triggers"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # emotional | environmental | social | temporal
    time_of_day: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    location_context: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
