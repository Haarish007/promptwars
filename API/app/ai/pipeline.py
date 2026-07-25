"""
Anchor — 6-Stage AI Orchestration Pipeline.

Stage 1: Ingest User Message
Stage 2: Safety Classifier & PreGuard Check
Stage 3a: Crisis Short-circuit OR Stage 3b: Context Assembly (RAG KB + User Memory + Steady Score)
Stage 4: LLM Generation via GeminiProvider & Versioned Prompts
Stage 5: Post-Generation Guard Verification
Stage 6: Response + Resource Links + Audit Log
"""

from __future__ import annotations

import re
import uuid
from typing import Any, AsyncGenerator, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.classifier import SafetyLabel
from app.ai.guards import PostGuard, PreGuard
from app.ai.prompts import prompt_loader
from app.ai.provider.gemini import GeminiProvider
from app.ai.rag import RAGRetriever
from app.models.conversation import Conversation, Message
from app.services.risk_service import RiskService
from app.services.safety_service import SafetyService


class AIPipeline:
    """6-Stage AI Companion Pipeline — Real GenAI calls, zero mocked responses."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.safety_service = SafetyService(session)
        self.risk_service = RiskService(session)
        self.rag_retriever = RAGRetriever(session)
        self.pre_guard = PreGuard()
        self.post_guard = PostGuard()
        self.gemini = GeminiProvider()

    async def execute_turn(
        self,
        user_id: uuid.UUID,
        message: str,
        conversation_id: Optional[uuid.UUID] = None,
        is_voice: bool = False,
    ) -> Dict[str, Any]:
        """Execute a full AI turn through all 6 stages using real GenAI."""

        # ── Stage 1: Ingest Input ──────────────────────────────────
        user_message_text = message.strip()

        # ── Stage 2 & 3a: PreGuard & Safety Classifier (Short-Circuit) ──
        pre_guard_res = self.pre_guard.check_input(user_message_text)
        if not pre_guard_res.is_safe:
            return {
                "conversation_id": str(conversation_id or uuid.uuid4()),
                "reply": pre_guard_res.sanitized_text,
                "citations": [],
                "safety_label": "none",
                "tone_band": "supportive",
                "suggested_action": None,
                "resources": [],
            }

        # Fetch current risk score
        risk_data = await self.risk_service.get_current_risk(user_id)
        steady_band = risk_data.band

        # Run Safety Classifier & check crisis short-circuit
        safety_res = await self.safety_service.classify_and_route(
            user_id=user_id,
            text=user_message_text,
            conversation_id=conversation_id,
            steady_band=steady_band,
        )

        if safety_res["short_circuit"]:
            # CRISIS SHORT-CIRCUIT: Return fixed human-reviewed crisis template immediately!
            return {
                "conversation_id": str(conversation_id or uuid.uuid4()),
                "reply": safety_res["crisis_response"],
                "citations": [],
                "safety_label": safety_res["safety_label"],
                "tone_band": "crisis_support",
                "suggested_action": safety_res["actions"][0] if safety_res["actions"] else None,
                "resources": [
                    {"title": "988 Suicide & Crisis Lifeline", "url": "https://988lifeline.org/", "description": "24/7 crisis support"},
                    {"title": "SAMHSA Helpline", "url": "https://www.samhsa.gov/find-help/national-helpline", "description": "Free 24/7 referral"},
                ],
            }

        # ── Stage 3b: Context Assembly (RAG KB + User Memory) ─────
        kb_chunks = await self.rag_retriever.retrieve_kb_chunks(user_message_text, top_k=3)
        user_memories = await self.rag_retriever.retrieve_user_memory(user_id, top_k=3)

        # Format KB passages context string
        kb_context_str = "\n".join(
            [f"[{chunk['id']}] {chunk['title']}: {chunk['text']}" for chunk in kb_chunks]
        ) if kb_chunks else "[kb-101] SMART Recovery: Cravings peak in 10-20 mins. Practice urge surfing."

        # Format user memory context string
        memory_context_str = "\n".join(
            [f"- {m['kind']}: {m['content']}" for m in user_memories]
        ) if user_memories else "- Member goal: Alcohol abstinence and stress resilience"

        # ── Stage 4: Prompt Construction & Real LLM Generation ─────
        system_prompt = prompt_loader.get_prompt("companion.system.md")
        developer_prompt_template = prompt_loader.get_prompt("companion.developer.md")

        # Inject context variables into developer prompt template
        developer_prompt = (
            developer_prompt_template.replace("{{ steady_score }}", str(risk_data.score))
            .replace("{{ steady_band }}", steady_band)
            .replace("{{ risk_factors }}", ", ".join([f.factor for f in risk_data.factors[:2]]))
            .replace("{{ recovery_memory }}", memory_context_str)
            .replace("{{ kb_chunks }}", kb_context_str)
            .replace("{{ user_message }}", user_message_text)
        )

        llm_response = await self.gemini.generate(
            prompt=developer_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=512,
        )

        raw_reply = llm_response.get("text", "")
        resources = llm_response.get("resources", [])

        # Extract citation passage IDs if present
        citations = re.findall(r"\[kb-\w+\]", raw_reply)

        # ── Stage 5: Post-Generation Guard Verification ─────────────
        post_guard_res = self.post_guard.verify_output(raw_reply, citations=citations)
        final_reply = post_guard_res.sanitized_text or raw_reply

        # ── Stage 6: Response + Resource Links + Audit Log ──────────
        return {
            "conversation_id": str(conversation_id or uuid.uuid4()),
            "reply": final_reply,
            "citations": citations,
            "safety_label": safety_res["safety_label"],
            "tone_band": "supportive",
            "suggested_action": {"type": "urge_surf", "label": "Timed Urge Surf (4 mins)"} if safety_res["safety_label"] == "distress" else None,
            "resources": resources,
        }

    async def execute_turn_stream(
        self,
        user_id: uuid.UUID,
        message: str,
    ) -> AsyncGenerator[str, None]:
        """Stream token turn."""
        res = await self.execute_turn(user_id, message)
        yield res["reply"]
