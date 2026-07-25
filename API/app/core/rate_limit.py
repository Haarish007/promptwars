"""
Anchor — In-memory sliding-window rate limiter.

Provides a FastAPI dependency factory for per-route-group rate limiting.
Returns 429 with the standard error envelope when exceeded.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable

from fastapi import HTTPException, Request

from app.core.config import settings
from app.core.logging import get_correlation_id


# ── Sliding Window Store ────────────────────────────────────────
class _SlidingWindowStore:
    """Simple in-memory sliding window counter keyed by (client_ip, group)."""

    def __init__(self) -> None:
        # key: (ip, group) -> list of timestamps
        self._hits: dict[tuple[str, str], list[float]] = defaultdict(list)

    def is_allowed(self, key: tuple[str, str], max_requests: int, window_seconds: int = 60) -> bool:
        now = time.monotonic()
        cutoff = now - window_seconds
        # Prune old entries
        self._hits[key] = [t for t in self._hits[key] if t > cutoff]
        if len(self._hits[key]) >= max_requests:
            return False
        self._hits[key].append(now)
        return True


_store = _SlidingWindowStore()


# ── Rate Limit Groups ──────────────────────────────────────────
_GROUP_LIMITS: dict[str, int] = {
    "auth": settings.rate_limit_auth_per_minute,
    "ai": settings.rate_limit_ai_per_minute,
    "sos": settings.rate_limit_sos_per_minute,
}


def rate_limit(group: str) -> Callable:
    """
    FastAPI dependency factory for rate limiting.

    Usage:
        @router.post("/auth/login", dependencies=[Depends(rate_limit("auth"))])
    """
    max_requests = _GROUP_LIMITS.get(group, 60)  # default 60/min

    async def _check_rate_limit(request: Request) -> None:
        # Use client IP as the key (X-Forwarded-For when behind Nginx)
        client_ip = request.headers.get(
            "x-forwarded-for", request.client.host if request.client else "unknown"
        )
        key = (client_ip, group)

        if not _store.is_allowed(key, max_requests):
            raise HTTPException(
                status_code=429,
                detail={
                    "error": {
                        "code": "rate_limited",
                        "message": "Too many requests. Please try again shortly.",
                        "correlation_id": get_correlation_id(),
                    }
                },
            )

    return _check_rate_limit
