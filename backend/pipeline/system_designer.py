"""Stage 2: System Designer — converts intent into architecture plan."""

import time
import json
from schemas.intent_schema import IntentSchema
from schemas.architecture_schema import ArchitectureSchema
from llm.provider import LLMProvider
from llm.prompts.templates import DESIGN_SYSTEM


class SystemDesigner:
    """Design system architecture from structured intent."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def design(self, intent: IntentSchema) -> tuple[ArchitectureSchema, int]:
        """Create architecture from intent. Returns (schema, duration_ms)."""
        start = time.time()
        user_msg = f"Design the system architecture for this intent:\n\n{json.dumps(intent.model_dump(), indent=2)}"
        raw = await self.provider.generate(DESIGN_SYSTEM, user_msg)
        result = ArchitectureSchema.model_validate(raw)
        duration = int((time.time() - start) * 1000)
        return result, duration
