"""
Anchor API v1 — Router registration.

All v1 routers are collected here and mounted under the API_V1_PREFIX.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    health,
    auth,
    consent,
    onboarding,
    checkin,
    risk,
    companion,
    safety,
    sos,
    urge,
    caregiver,
    kb,
    tracking,
    notifications,
    demo,
)

api_v1_router = APIRouter()

# ── Active routers ──────────────────────────────────────────────
api_v1_router.include_router(health.router, tags=["health"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_v1_router.include_router(consent.router, prefix="/consents", tags=["consent"])
api_v1_router.include_router(onboarding.router, prefix="/onboarding", tags=["onboarding"])
api_v1_router.include_router(checkin.router, prefix="/checkins", tags=["check-in"])
api_v1_router.include_router(risk.router, prefix="/risk", tags=["risk"])
api_v1_router.include_router(companion.router, prefix="/companion", tags=["companion"])
api_v1_router.include_router(safety.router, prefix="/safety", tags=["safety"])
api_v1_router.include_router(sos.router, prefix="/sos", tags=["sos"])
api_v1_router.include_router(urge.router, prefix="/interventions", tags=["urge"])
api_v1_router.include_router(caregiver.router, prefix="/caregiver", tags=["caregiver"])
api_v1_router.include_router(kb.router, prefix="/kb", tags=["knowledge-base"])
api_v1_router.include_router(tracking.router, tags=["tracking"])
api_v1_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_v1_router.include_router(demo.router, prefix="/demo", tags=["demo"])
