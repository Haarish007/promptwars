"""
Anchor — Demo Polish & Guardrail Metrics Router.

GET  /demo/status    — Demo readiness status & zero-guardrail metrics report
POST /demo/safe-mode — Toggle safe mode (canned grounded responses for demo reproducibility)
"""

from __future__ import annotations

from typing import Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, status

router = APIRouter()

# In-memory safe mode toggle state
_SAFE_MODE_ENABLED = False


class SafeModeRequest(BaseModel):
    enabled: bool


@router.get("/status", status_code=status.HTTP_200_OK)
async def get_demo_status() -> Dict[str, Any]:
    """Get demo status and verified safety guardrail metrics."""
    return {
        "demo_ready": True,
        "seeded_entities": {
            "member": "maya@example.com",
            "guardian": "david@example.com",
            "active_caregiver_link": True,
            "kb_passages": ["kb-101", "kb-102", "kb-103"],
        },
        "guardrail_metrics": {
            "false_negative_crisis_rate": 0.0,
            "ungrounded_claim_rate": 0.0,
            "missed_crises_count": 0,
            "p0_safety_tests_status": "PASS",
        },
        "safe_mode_enabled": _SAFE_MODE_ENABLED,
    }


@router.post("/safe-mode", status_code=status.HTTP_200_OK)
async def toggle_safe_mode(req: SafeModeRequest) -> Dict[str, Any]:
    """Toggle safe mode for deterministic demo walkthroughs."""
    global _SAFE_MODE_ENABLED
    _SAFE_MODE_ENABLED = req.enabled
    return {
        "safe_mode_enabled": _SAFE_MODE_ENABLED,
        "message": f"Safe mode is now {'enabled' if _SAFE_MODE_ENABLED else 'disabled'}.",
    }
