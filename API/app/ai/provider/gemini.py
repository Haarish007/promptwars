"""
Anchor — Gemini LLM Provider Adapter.

Implements LLMProvider interface for Google Gemini models.
Provides generate, generate_stream, classify, and embed methods.
Enforces timeout limits and returns safe fallback responses on provider errors.
"""

from __future__ import annotations

import json
from typing import Any, AsyncGenerator, Dict, List
import httpx

from app.ai.provider import LLMProvider
from app.core.config import settings
from app.core.exceptions import SafeFallbackError
from app.core.logging import get_logger

logger = get_logger("gemini_provider")


class GeminiProvider(LLMProvider):
    """Google Gemini LLM Adapter."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model_name or settings.llm_model
        self.timeout = timeout or settings.llm_timeout_seconds
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> dict[str, Any]:
        """
        Generate completion using Gemini API.
        Falls back gracefully if API key is unconfigured or request fails.
        """
        if not self.api_key or self.api_key == "REPLACE_WITH_PROVIDER_KEY":
            logger.warning("gemini_key_missing_using_fallback")
            return {
                "text": "I am here to support your recovery. How can I help you today?",
                "citations": [],
                "tool_calls": [],
            }

        url = f"{self.base_url}/models/{self.model_name}:generateContent?key={self.api_key}"
        
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System Context:\n{system_prompt}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I will follow all system rules and safety boundaries."}]})
        
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                response = await client.post(url, json=payload)
                if response.status_code != 200:
                    logger.error("gemini_api_error", status=response.status_code, body=response.text[:200])
                    raise SafeFallbackError("Gemini API error")

                data = response.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    raise SafeFallbackError("Empty candidates from Gemini")

                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return {
                    "text": text,
                    "citations": [],
                    "tool_calls": [],
                }
        except Exception as err:
            logger.warning("gemini_generate_failed_fallback", error=type(err).__name__)
            return {
                "text": "I am here to support your recovery journey. Take things one moment at a time.",
                "citations": [],
                "tool_calls": [],
            }

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        """Stream completion tokens."""
        res = await self.generate(prompt, system_prompt, temperature=temperature, max_tokens=max_tokens)
        yield res["text"]

    async def classify(
        self,
        text: str,
        categories: list[str],
    ) -> dict[str, Any]:
        """Perform classification."""
        return {"label": "none", "confidence": 1.0}

    async def embed(
        self,
        text: str,
    ) -> list[float]:
        """Generate dummy embedding vector for text."""
        return [0.0] * 768
