"""
Anchor — Check-in API Router.

POST /checkins — Submit daily check-in (mood, sleep, craving, HALT, note). Returns recomputed score & suggested action.
GET  /checkins — Get historical check-in trend series.
"""

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.checkin import CheckInResponse, CheckInSubmitRequest, CheckInSubmitResponse
from app.services.checkin_service import CheckInService

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CheckInSubmitResponse)
async def submit_checkin(
    req: CheckInSubmitRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit daily check-in.
    Encrypts note at rest, recomputes Steady Score, returns top factors & suggested action.
    """
    service = CheckInService(db)
    return await service.submit_checkin(current_user.id, req)


@router.get("", response_model=List[CheckInResponse])
async def get_checkin_trend(
    limit: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get check-in trend history for current user."""
    service = CheckInService(db)
    return await service.get_checkin_trend(current_user.id, limit)
