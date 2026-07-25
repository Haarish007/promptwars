"""
Anchor — Domain exceptions and error envelope.

Defines a hierarchy of domain errors mapped to HTTP status codes.
Error envelope format per docs/07:
  {"error": {"code": "string", "message": "human-safe message", "correlation_id": "uuid"}}

Never leaks stack traces or provider errors to the client.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_correlation_id, get_logger

logger = get_logger("exceptions")


# ── Domain Exception Hierarchy ──────────────────────────────────
class AnchorError(Exception):
    """Base domain exception. All Anchor errors extend this."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        code: str = "internal_error",
        status_code: int = 500,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AnchorError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, code="not_found", status_code=404)


class ConflictError(AnchorError):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message=message, code="conflict", status_code=409)


class ForbiddenError(AnchorError):
    def __init__(self, message: str = "Access denied"):
        super().__init__(message=message, code="forbidden", status_code=403)


class ValidationError(AnchorError):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message=message, code="validation_error", status_code=422)


class UnauthorizedError(AnchorError):
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(message=message, code="unauthorized", status_code=401)


class RateLimitedError(AnchorError):
    def __init__(self, message: str = "Too many requests"):
        super().__init__(message=message, code="rate_limited", status_code=429)


class DependencyUnavailableError(AnchorError):
    def __init__(self, message: str = "A required service is unavailable"):
        super().__init__(
            message=message, code="dependency_unavailable", status_code=503
        )


class SafeFallbackError(AnchorError):
    """Used when the AI provider fails and we return a safe canned response."""

    def __init__(self, message: str = "Using safe fallback response"):
        super().__init__(message=message, code="safe_fallback", status_code=200)


# ── Error Envelope Builder ──────────────────────────────────────
def _build_error_envelope(code: str, message: str) -> dict:
    """Build the standard error response envelope per docs/07."""
    return {
        "error": {
            "code": code,
            "message": message,
            "correlation_id": get_correlation_id(),
        }
    }


# ── Exception Handlers ─────────────────────────────────────────
def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI app."""

    @app.exception_handler(AnchorError)
    async def anchor_error_handler(request: Request, exc: AnchorError) -> JSONResponse:
        logger.warning(
            "domain_error",
            code=exc.code,
            status=exc.status_code,
            # Never log the message content — it may contain user context
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_build_error_envelope(exc.code, exc.message),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Catch-all: never expose stack traces or internal details."""
        logger.error(
            "unhandled_exception",
            exc_type=type(exc).__name__,
            # Do NOT log exc message — may contain provider secrets or PII
        )
        return JSONResponse(
            status_code=500,
            content=_build_error_envelope(
                "internal_error",
                "An unexpected error occurred. Please try again.",
            ),
        )
