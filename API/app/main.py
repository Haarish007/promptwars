"""
Anchor — FastAPI App Factory.

Registers routers, middleware, exception handlers, and lifecycle events.
Runs behind Nginx on /promptwars (port 8100).
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import CorrelationIdMiddleware, get_logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle context manager."""
    setup_logging(settings.log_level)
    logger = get_logger("main")
    logger.info(
        "app_starting",
        env=settings.app_env,
        host=settings.backend_host,
        port=settings.backend_port,
    )
    yield
    logger.info("app_stopping")


def create_app() -> FastAPI:
    """FastAPI app factory."""
    app = FastAPI(
        title="Anchor API",
        description="AI-powered proactive recovery and prevention platform backend",
        version="1.0.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── Correlation ID Middleware (first in pipeline) ────────────
    app.add_middleware(CorrelationIdMiddleware)

    # ── CORS Middleware (Permissive Wildcard * for cross-origin requests) ──
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Register Exception Handlers ─────────────────────────────
    register_exception_handlers(app)

    # ── Mount API Routers (Mount under /v1 and settings.api_v1_prefix for Nginx rewrite compatibility) ──
    app.include_router(api_v1_router, prefix="/v1")
    if settings.api_v1_prefix and settings.api_v1_prefix != "/v1":
        app.include_router(api_v1_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
