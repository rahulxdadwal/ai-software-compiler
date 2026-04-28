"""LLM provider abstraction — supports OpenAI and mock mode."""

from __future__ import annotations
import json
import os
from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> dict:
        """Generate structured JSON from prompts."""
        ...


class OpenAIProvider(LLMProvider):
    """OpenAI API provider with low temperature for determinism."""

    def __init__(self, api_key: str, model: str = "gpt-4o", temperature: float = 0.1):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature

    async def generate(self, system_prompt: str, user_prompt: str) -> dict:
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        text = response.choices[0].message.content or "{}"
        return json.loads(text)


class MockProvider(LLMProvider):
    """Deterministic mock provider for demo without API key."""

    def __init__(self):
        from mock.mock_responses import get_mock_response
        self._get_mock = get_mock_response

    async def generate(self, system_prompt: str, user_prompt: str) -> dict:
        stage = "unknown"
        lower_prompt = system_prompt.lower()
        if "intent extraction engine" in lower_prompt:
            stage = "intent"
        elif "architecture designer" in lower_prompt:
            stage = "architecture"
        elif "ui schema generator" in lower_prompt:
            stage = "ui_schema"
        elif "api schema generator" in lower_prompt:
            stage = "api_schema"
        elif "database schema generator" in lower_prompt:
            stage = "db_schema"
        elif "auth schema generator" in lower_prompt:
            stage = "auth_schema"
        elif "business rules generator" in lower_prompt:
            stage = "business_rules"
        elif "repair engine" in lower_prompt:
            stage = "repair"
        return self._get_mock(stage, user_prompt)


def create_provider() -> LLMProvider:
    """Factory: returns OpenAI provider if key exists, else mock."""
    from config import settings
    if settings.use_mock:
        return MockProvider()
    return OpenAIProvider(
        api_key=settings.openai_api_key or "",
        model=settings.openai_model,
        temperature=settings.llm_temperature,
    )
