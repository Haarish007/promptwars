"""
Anchor — LLM Provider Interface.

Defines the abstract base class for LLM adapters (e.g. Gemini).
Enables swappable LLM providers while keeping business logic provider-agnostic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator


class LLMProvider(ABC):
    """Abstract interface for LLM operations."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> dict[str, Any]:
        """
        Generate a completion.
        Returns response envelope with text, tool calls, token usage.
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        """Stream completion tokens asynchronously."""
        pass

    @abstractmethod
    async def classify(
        self,
        text: str,
        categories: list[str],
    ) -> dict[str, Any]:
        """Perform strict JSON classification."""
        pass

    @abstractmethod
    async def embed(
        self,
        text: str,
    ) -> list[float]:
        """Generate vector embedding for text."""
        pass
