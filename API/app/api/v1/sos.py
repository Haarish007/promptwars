"""
Anchor — SOS Crisis API Router.

POST /sos — Immediate zero-typing crisis support payload (<500ms response).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import rate_limit
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.sos import SOSRequest, SOSResponse
from app.services.sos_service import SOSService

router = APIRouter()


@router.post("", response_model=SOSResponse, dependencies=[Depends(rate_limit("sos"))])
async def trigger_sos(
    req: SOSRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger zero-typing crisis intervention flow (<500ms target).
    Resolves emergency contacts, region crisis lines, one-tap call/urge-surf actions, and audits safety event.
    """
    service = SOSService(db)
    return await service.trigger_sos(current_user.id, req)
