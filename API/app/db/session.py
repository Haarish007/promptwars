"""
Anchor — Database Session Factory.

Creates SQLAlchemy engine and session factory. Supports both asyncpg and psycopg2
drivers to handle environments where C-extension DLLs (asyncpg) may be restricted.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


def _build_engine():
    db_url = settings.database_url
    try:
        # Try asyncpg engine
        if db_url.startswith("postgresql+asyncpg://"):
            import asyncpg.protocol  # test DLL load
            async_eng = create_async_engine(
                db_url,
                pool_size=settings.db_pool_size,
                max_overflow=settings.db_max_overflow,
                echo=(settings.app_env == "development"),
            )
            return async_eng, True
    except Exception:
        pass

    # Fallback to psycopg2 sync engine for environments where asyncpg DLL is blocked
    sync_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    sync_eng = create_engine(
        sync_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        echo=(settings.app_env == "development"),
    )
    return sync_eng, False


engine, is_async = _build_engine()

if is_async:
    async_session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
else:
    sync_session_factory = sessionmaker(
        bind=engine,
        class_=Session,
        expire_on_commit=False,
    )
    # Async wrapper around sync session factory
    class _AsyncSessionWrapper:
        def __init__(self, sync_session: Session):
            self._session = sync_session

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                self._session.rollback()
            self._session.close()

        def add(self, instance):
            self._session.add(instance)

        def add_all(self, instances):
            self._session.add_all(instances)

        async def flush(self):
            self._session.flush()

        async def commit(self):
            self._session.commit()

        async def rollback(self):
            self._session.rollback()

        async def execute(self, statement, *args, **kwargs):
            return self._session.execute(statement, *args, **kwargs)

    class _AsyncSessionFactoryWrapper:
        def __call__(self):
            return _AsyncSessionWrapper(sync_session_factory())

    async_session_factory = _AsyncSessionFactoryWrapper()


# ── FastAPI Dependency ──────────────────────────────────────────
async def get_db() -> AsyncGenerator:
    """Yield a request-scoped database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
