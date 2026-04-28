"""Stage 3: Schema Generator — produces UI, API, DB, Auth, BusinessRules schemas."""

import time
import json
from schemas.architecture_schema import ArchitectureSchema
from schemas.ui_schema import UISchema
from schemas.api_schema import APISchema
from schemas.db_schema import DBSchema
from schemas.auth_schema import AuthSchema
from schemas.business_rules_schema import BusinessRulesSchema
from llm.provider import LLMProvider
from llm.prompts.templates import (
    SCHEMA_UI_SYSTEM, SCHEMA_API_SYSTEM, SCHEMA_DB_SYSTEM,
    SCHEMA_AUTH_SYSTEM, SCHEMA_BUSINESS_SYSTEM,
)


class SchemaGenerator:
    """Generate all five sub-schemas from architecture plan."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def _generate_one(self, system_prompt: str, arch_json: str) -> dict:
        user_msg = f"Generate schema from this architecture:\n\n{arch_json}"
        return await self.provider.generate(system_prompt, user_msg)

    async def generate(self, architecture: ArchitectureSchema) -> tuple[dict, int]:
        """Generate all schemas. Returns ({name: schema}, duration_ms)."""
        start = time.time()
        arch_json = json.dumps(architecture.model_dump(), indent=2)

        ui_raw = await self._generate_one(SCHEMA_UI_SYSTEM, arch_json)
        api_raw = await self._generate_one(SCHEMA_API_SYSTEM, arch_json)
        db_raw = await self._generate_one(SCHEMA_DB_SYSTEM, arch_json)
        auth_raw = await self._generate_one(SCHEMA_AUTH_SYSTEM, arch_json)
        biz_raw = await self._generate_one(SCHEMA_BUSINESS_SYSTEM, arch_json)

        schemas = {
            "ui": UISchema.model_validate(ui_raw),
            "api": APISchema.model_validate(api_raw),
            "db": DBSchema.model_validate(db_raw),
            "auth": AuthSchema.model_validate(auth_raw),
            "business_rules": BusinessRulesSchema.model_validate(biz_raw),
        }
        duration = int((time.time() - start) * 1000)
        return schemas, duration
