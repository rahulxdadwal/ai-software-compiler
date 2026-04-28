"""Stage 1: Intent Extraction — parses raw NL prompt into structured intent."""

import time
from schemas.intent_schema import IntentSchema
from llm.provider import LLMProvider
from llm.prompts.templates import INTENT_SYSTEM


class IntentExtractor:
    """Extract structured intent from a natural language prompt."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def extract(self, prompt: str) -> tuple[IntentSchema, int]:
        """Extract intent from prompt. Returns (schema, duration_ms)."""
        start = time.time()
        user_msg = f"Extract structured intent from this product prompt:\n\n{prompt}"
        raw = await self.provider.generate(INTENT_SYSTEM, user_msg)
        # Ensure raw_prompt is set
        raw["raw_prompt"] = prompt
        result = IntentSchema.model_validate(raw)
        duration = int((time.time() - start) * 1000)
        return result, duration
