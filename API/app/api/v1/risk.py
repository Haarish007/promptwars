"""
Anchor — Risk / Steady Score API Router.

GET /risk/current — Get current Steady Score, band, and top factors.
GET /risk/history — Get score snapshot history.
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.risk import RiskScoreResponse
from app.services.risk_service import RiskService

router = APIRouter()


@router.get("/current", response_model=RiskScoreResponse)
async def get_current_risk(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current explainable Steady Score, band, and factors."""
    service = RiskService(db)
    return await service.get_current_risk(current_user.id)


@router.get("/history", response_model=List[RiskScoreResponse])
async def get_risk_history(
    limit: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get score snapshot history."""
    service = RiskService(db)
    return await service.get_risk_history(current_user.id, limit)
