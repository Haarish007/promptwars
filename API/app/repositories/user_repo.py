"""
Anchor — User & Profile Repository.
"""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, RefreshToken
from app.models.profile import MemberProfile, EmergencyContact, Trigger


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower(), User.deleted_at.is_(None))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_profile(self, user_id: uuid.UUID) -> MemberProfile | None:
        stmt = select(MemberProfile).where(MemberProfile.user_id == user_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def save_profile(self, profile: MemberProfile) -> MemberProfile:
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def add_emergency_contact(self, contact: EmergencyContact) -> EmergencyContact:
        self.session.add(contact)
        await self.session.flush()
        return contact

    async def get_emergency_contacts(self, user_id: uuid.UUID) -> Sequence[EmergencyContact]:
        stmt = select(EmergencyContact).where(EmergencyContact.user_id == user_id).order_by(EmergencyContact.priority)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def save_refresh_token(self, token: RefreshToken) -> RefreshToken:
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_refresh_token_by_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
