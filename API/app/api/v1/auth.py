"""
Anchor — Auth API Router.

POST /auth/register
POST /auth/login (rate-limited)
POST /auth/refresh
POST /auth/logout
GET  /auth/me
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import rate_limit
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user account (Argon2id password hashing + default consent)."""
    service = AuthService(db)
    return await service.register(req)


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(rate_limit("auth"))])
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate with email and password. Returns access + rotating refresh token pair."""
    service = AuthService(db)
    return await service.login(req)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Rotate refresh token: issues new access + refresh token, revoking the prior token."""
    service = AuthService(db)
    return await service.refresh_token(req.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Revoke the provided refresh token."""
    service = AuthService(db)
    await service.logout(req.refresh_token)
    return None


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return current authenticated user profile."""
    return current_user
