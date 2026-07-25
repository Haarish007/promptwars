"""
Anchor — Consent Service.

Manages explicit, versioned, revocable consent for data processing and caregiver sharing.
"""

from __future__ import annotations

import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError
from app.models.consent import Consent
from app.repositories.consent_repo import ConsentRepository
from app.schemas.consent import ConsentGrantRequest


class ConsentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.consent_repo = ConsentRepository(session)

    async def grant_consent(self, user_id: uuid.UUID, req: ConsentGrantRequest) -> Consent:
        consent = Consent(
            user_id=user_id,
            scope=req.scope,
            version=req.version,
        )
        return await self.consent_repo.grant_consent(consent)

    async def revoke_consent(self, user_id: uuid.UUID, scope: str) -> bool:
        return await self.consent_repo.revoke_consent(user_id, scope)

    async def list_consents(self, user_id: uuid.UUID) -> Sequence[Consent]:
        return await self.consent_repo.get_active_consents(user_id)

    async def enforce_consent(self, user_id: uuid.UUID, scope: str) -> None:
        """Enforces 'no share without active consent' rule."""
        has_consent = await self.consent_repo.has_active_consent(user_id, scope)
        if not has_consent:
            raise ForbiddenError(f"User has not granted active consent for scope: {scope}")
