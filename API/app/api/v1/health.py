"""
Anchor — Health & Readiness API Router.

GET /health       — Basic healthcheck (DB ping + safety classifier probe)
GET /health/ready — Readiness probe for deployment gating
"""

from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.classifier import SafetyClassifier
from app.db.session import get_db

router = APIRouter()
classifier = SafetyClassifier()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Healthcheck endpoint verifying DB connection and safety classifier status."""
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as err:
        db_status = f"error: {type(err).__name__}"

    # Safety classifier probe
    probe = classifier.deterministic_pre_filter("I am having a good day")
    classifier_status = "healthy" if probe is None else "degraded"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "safety_classifier": classifier_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Deployment readiness probe."""
    await db.execute(text("SELECT 1"))
    return {
        "ready": True,
        "service": "anchor-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
