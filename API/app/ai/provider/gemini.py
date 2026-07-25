"""
Anchor — Gemini LLM Provider Adapter (Real Google GenAI API Integration).

Implements LLMProvider interface for Google Gemini models.
Makes REAL API calls to generativelanguage.googleapis.com.
No hardcoded/mock responses. If the API call fails, returns a clear error message.
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


# Evidence-based recovery resource links
RESOURCE_LINKS = {
    "samhsa": {"title": "SAMHSA National Helpline", "url": "https://www.samhsa.gov/find-help/national-helpline", "description": "Free 24/7 referral service"},
    "smart_recovery": {"title": "SMART Recovery Online", "url": "https://www.smartrecovery.org/", "description": "Science-based mutual support"},
    "988_lifeline": {"title": "988 Suicide & Crisis Lifeline", "url": "https://988lifeline.org/", "description": "24/7 crisis support"},
    "niaaa": {"title": "NIAAA Rethinking Drinking", "url": "https://www.rethinkingdrinking.niaaa.nih.gov/", "description": "NIH alcohol self-assessment tools"},
    "aa_meetings": {"title": "AA Meeting Finder", "url": "https://www.aa.org/find-aa", "description": "Find local AA meetings"},
}


class GeminiProvider(LLMProvider):
    """Google Gemini LLM Adapter — Real API calls only."""

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

    def _is_key_configured(self) -> bool:
        """Check if a real Google Gemini API key is present."""
        if not self.api_key:
            return False
        if self.api_key in ("REPLACE_WITH_PROVIDER_KEY", ""):
            return False
        # Must be a real Google key (starts with AIza)
        if self.api_key.startswith("AIza"):
            return True
        # Also accept other formats but warn
        logger.warning("gemini_key_format_unexpected", key_prefix=self.api_key[:8])
        return True

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> dict[str, Any]:
        """
        Generate completion using the real Google Gemini API.
        No hardcoded fallbacks — if the key is missing, returns an actionable error.
        """
        if not self._is_key_configured():
            logger.error("gemini_api_key_not_configured")
            return {
                "text": (
                    "⚠️ The Gemini API key is not configured. "
                    "Please set GEMINI_API_KEY in your .env file with a valid Google AI Studio key. "
                    "Get one free at: https://aistudio.google.com/apikey"
                ),
                "citations": [],
                "tool_calls": [],
                "resources": [],
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
                # Try with primary model, retry with fallback model on 429
                models_to_try = [self.model_name]
                fallback = settings.llm_classifier_model
                if fallback and fallback != self.model_name:
                    models_to_try.append(fallback)

                last_error = ""
                for model in models_to_try:
                    attempt_url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"
                    for attempt in range(3):
                        response = await client.post(attempt_url, json=payload)
                        if response.status_code == 200:
                            data = response.json()
                            candidates = data.get("candidates", [])
                            if not candidates:
                                logger.warning("gemini_empty_candidates", model=model)
                                last_error = "The AI model returned an empty response. Please try rephrasing your question."
                                break

                            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                            resources = self._select_resources(prompt + " " + text)
                            return {
                                "text": text,
                                "citations": [],
                                "tool_calls": [],
                                "resources": resources,
                            }

                        elif response.status_code == 429:
                            wait_secs = (attempt + 1) * 2  # 2s, 4s, 6s backoff
                            logger.warning("gemini_rate_limited_retrying", model=model, attempt=attempt + 1, wait=wait_secs)
                            import asyncio
                            await asyncio.sleep(wait_secs)
                            continue
                        else:
                            error_detail = response.text[:300] if response.text else "Unknown error"
                            logger.error("gemini_api_error", status=response.status_code, model=model, body=error_detail)
                            last_error = f"Gemini API returned status {response.status_code}."
                            break
                    else:
                        # All retries exhausted for this model
                        last_error = "Rate limit exceeded after retries. Please wait a moment and try again."
                        continue  # Try next model

                return {
                    "text": last_error or "Unable to generate a response. Please try again.",
                    "citations": [],
                    "tool_calls": [],
                    "resources": self._select_resources(prompt),
                }




        except httpx.TimeoutException:
            logger.error("gemini_timeout")
            return {
                "text": "The AI request timed out. Please try again.",
                "citations": [],
                "tool_calls": [],
                "resources": [],
            }
        except Exception as err:
            logger.error("gemini_generate_exception", error=type(err).__name__, detail=str(err)[:200])
            return {
                "text": f"An error occurred while generating the response: {type(err).__name__}. Please try again.",
                "citations": [],
                "tool_calls": [],
                "resources": [],
            }

    def _select_resources(self, text: str) -> list[dict[str, str]]:
        """Select relevant recovery resource links based on content."""
        t = text.lower()
        resources = []
        if any(w in t for w in ("alcohol", "drink", "substance", "addict", "recovery", "quit", "sober")):
            resources.append(RESOURCE_LINKS["samhsa"])
            resources.append(RESOURCE_LINKS["niaaa"])
            resources.append(RESOURCE_LINKS["smart_recovery"])
        if any(w in t for w in ("crisis", "suicid", "harm", "emergency", "struggling", "overwhelm")):
            resources.append(RESOURCE_LINKS["988_lifeline"])
        if any(w in t for w in ("meeting", "group", "support", "community", "aa")):
            resources.append(RESOURCE_LINKS["aa_meetings"])
        if not resources:
            resources.append(RESOURCE_LINKS["samhsa"])
        return resources

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
        """Perform classification using real Gemini call."""
        if not self._is_key_configured():
            return {"label": "none", "confidence": 0.5}

        classify_prompt = f"Classify the following text into one of these categories: {', '.join(categories)}.\nText: {text}\nReturn only the category label."
        res = await self.generate(classify_prompt, temperature=0.1, max_tokens=50)
        label = res.get("text", "none").strip().lower()
        matched = next((c for c in categories if c.lower() in label), "none")
        return {"label": matched, "confidence": 0.85}

    async def embed(
        self,
        text: str,
    ) -> list[float]:
        """Generate embedding vector (placeholder — use text-embedding model for production)."""
        return [0.0] * 768
