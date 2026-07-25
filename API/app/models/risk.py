"""
Anchor — Risk Score & Risk Config ORM Models.
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, SmallInteger, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class RiskScore(Base, TimestampMixin):
    __tablename__ = "risk_scores"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    band: Mapped[str] = mapped_column(String(20), nullable=False)  # low | guarded | elevated | high
    factors: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=list)
    checkin_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("check_ins.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="chk_risk_score_range"),
        Index("ix_risk_scores_user_created", "user_id", "created_at"),
    )


class RiskConfig(Base, TimestampMixin):
    __tablename__ = "risk_config"

    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    weights: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
