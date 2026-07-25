"""
Anchor — Structured JSON Logging & PII Scrubbing.

Provides:
  - structlog JSON output with correlation ID tracking
  - PII Scrubbing Processor (redacts phone numbers, emails, notes, auth headers)
  - CorrelationIdMiddleware for HTTP request correlation tracking
"""

from __future__ import annotations

import logging
import re
import sys
import uuid
from contextvars import ContextVar
from typing import Any, Dict

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# ContextVar for request correlation ID
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


def set_correlation_id(cid: str) -> None:
    correlation_id_var.set(cid)


def get_correlation_id() -> str:
    return correlation_id_var.get()


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware that injects or propagates X-Correlation-ID header."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        cid = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        set_correlation_id(cid)
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = cid
        return response


# ── PII Scrubbing Processor ──────────────────────────────────────────
PHONE_REGEX = re.compile(r"(?<![a-fA-F0-9\-])(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?![a-fA-F0-9\-])")
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


def scrub_pii_processor(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    structlog processor that scrubs PII (phone numbers, emails, sensitive fields).
    Satisfies TC-LOG-002 requirements.
    """
    sensitive_keys = {"note", "notes", "transcript", "phone", "phone_number", "authorization", "password", "token"}

    for key, value in list(event_dict.items()):
        key_lower = key.lower()

        # Direct sensitive field match
        if key_lower in sensitive_keys:
            event_dict[key] = "[REDACTED]"
            continue

        # Regex check on string values
        if isinstance(value, str):
            val = EMAIL_REGEX.sub("[REDACTED]", value)
            val = PHONE_REGEX.sub("[REDACTED]", val)
            event_dict[key] = val

    # Add correlation ID to every log record
    cid = get_correlation_id()
    if cid:
        event_dict["correlation_id"] = cid

    return event_dict


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structlog with JSON renderer & PII scrubbing."""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            scrub_pii_processor,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "anchor") -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
