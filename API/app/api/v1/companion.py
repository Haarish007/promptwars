"""
Anchor — AI Companion API Router.

POST /companion/chat        — Execute single-turn AI companion response through 6-stage pipeline.
POST /companion/chat/stream — SSE streaming response endpoint.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.pipeline import AIPipeline
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: Optional[uuid.UUID] = None
    is_voice: bool = False


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    citations: list[str] = []
    safety_label: str
    tone_band: str
    suggested_action: Optional[dict] = None
    resources: Optional[list] = None


@router.post("/chat", response_model=ChatResponse)
async def chat_turn(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute AI companion interaction.
    Runs inbound input through the 6-Stage Pipeline (Safety, RAG, Gemini, PostGuards).
    """
    pipeline = AIPipeline(db)
    result = await pipeline.execute_turn(
        user_id=current_user.id,
        message=req.message,
        conversation_id=req.conversation_id,
        is_voice=req.is_voice,
    )
    return result


@router.post("/chat/stream")
async def chat_turn_stream(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stream AI companion completion tokens via SSE."""
    pipeline = AIPipeline(db)

    async def _event_generator():
        async for token in pipeline.execute_turn_stream(user_id=current_user.id, message=req.message):
            yield f"data: {token}\n\n"

    return StreamingResponse(_event_generator(), media_type="text/event-stream")
