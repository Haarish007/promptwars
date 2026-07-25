"""
Anchor — Safety API Router.

POST /safety/classify — Classify inbound message and return safety label, tier, & short-circuit response.
GET  /resources       — Get region-appropriate crisis resources.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.safety_service import SafetyService

router = APIRouter()


class ClassifyRequest(BaseModel):
    content: str
    region: Optional[str] = None
    steady_band: Optional[str] = "low"


@router.post("/classify")
async def classify_message(
    req: ClassifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Classify inbound text message and determine safety routing.
    If crisis/self_harm/medical -> returns short-circuit fixed response & resources.
    Audits safety event to DB.
    """
    service = SafetyService(db)
    return await service.classify_and_route(
        user_id=current_user.id,
        text=req.content,
        region=req.region,
        steady_band=req.steady_band or "low",
    )


@router.get("/resources")
async def get_resources(
    region: Optional[str] = Query(None, description="Region code (e.g. US, IN)"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get region-appropriate crisis resources."""
    service = SafetyService(db)
    resources = service.get_region_resources(region)
    return {"region": region or "US", "resources": resources}
