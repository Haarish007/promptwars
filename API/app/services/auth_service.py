"""
Anchor — Auth Service.

Handles user registration, login, rotating refresh token exchange, revocation, and user retrieval.
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.consent import Consent
from app.models.user import RefreshToken, User
from app.repositories.consent_repo import ConsentRepository
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.consent_repo = ConsentRepository(session)

    async def register(self, req: RegisterRequest) -> User:
        existing = await self.user_repo.get_by_email(req.email)
        if existing:
            raise ConflictError("Email is already registered")

        user = User(
            email=req.email.lower(),
            password_hash=hash_password(req.password),
            role=req.role,
            status="active",
        )
        await self.user_repo.create_user(user)

        # Record default data_processing consent on registration
        consent = Consent(
            user_id=user.id,
            scope="data_processing",
            version="1.0",
        )
        await self.consent_repo.grant_consent(consent)

        return user

    async def login(self, req: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(req.email)
        if not user or not verify_password(req.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        if user.status != "active":
            raise UnauthorizedError("User account is suspended or deleted")

        user.last_login_at = datetime.now(timezone.utc)

        # Generate token pair
        access_token = create_access_token(str(user.id), user.role)
        raw_refresh_token = create_refresh_token(str(user.id))

        # Store hashed refresh token in database
        token_hash = hash_token(raw_refresh_token)
        refresh_entity = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc)
            + settings.refresh_token_ttl_days * timedelta_days(1),
        )
        await self.user_repo.save_refresh_token(refresh_entity)

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            expires_in=settings.access_token_ttl_minutes * 60,
        )

    async def refresh_token(self, raw_refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(raw_refresh_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedError("Invalid token type")
            user_id_str = payload.get("sub")
            if not user_id_str:
                raise UnauthorizedError("Invalid refresh token payload")
        except Exception:
            raise UnauthorizedError("Invalid or expired refresh token")

        token_h = hash_token(raw_refresh_token)
        token_entity = await self.user_repo.get_refresh_token_by_hash(token_h)
        if not token_entity:
            raise UnauthorizedError("Refresh token not found")

        # Security check: if token was already revoked, flag as potential reuse breach!
        if token_entity.revoked_at is not None:
            raise UnauthorizedError("Refresh token has been revoked")

        now = datetime.now(timezone.utc)
        if token_entity.expires_at < now:
            raise UnauthorizedError("Refresh token expired")

        user = await self.user_repo.get_by_id(token_entity.user_id)
        if not user or user.status != "active":
            raise UnauthorizedError("User inactive")

        # Rotate tokens: create new refresh token, mark old revoked & replaced_by
        new_access_token = create_access_token(str(user.id), user.role)
        new_raw_refresh_token = create_refresh_token(str(user.id))

        new_token_hash = hash_token(new_raw_refresh_token)
        new_token_entity = RefreshToken(
            user_id=user.id,
            token_hash=new_token_hash,
            expires_at=now + settings.refresh_token_ttl_days * timedelta_days(1),
        )
        await self.user_repo.save_refresh_token(new_token_entity)

        token_entity.revoked_at = now
        token_entity.replaced_by = new_token_entity.id

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_raw_refresh_token,
            expires_in=settings.access_token_ttl_minutes * 60,
        )

    async def logout(self, raw_refresh_token: str) -> None:
        token_h = hash_token(raw_refresh_token)
        token_entity = await self.user_repo.get_refresh_token_by_hash(token_h)
        if token_entity and token_entity.revoked_at is None:
            token_entity.revoked_at = datetime.now(timezone.utc)


def timedelta_days(days: int):
    from datetime import timedelta
    return timedelta(days=days)
