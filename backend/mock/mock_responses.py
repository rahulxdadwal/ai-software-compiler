"""Mock response dispatcher — returns deterministic outputs per stage."""

from mock.mock_data_part1 import CRM_INTENT, CRM_ARCHITECTURE
from mock.mock_data_part2 import CRM_UI, CRM_API
from mock.mock_data_part3 import CRM_DB, CRM_AUTH, CRM_BUSINESS_RULES
import copy


# Map stage names to mock data
_MOCK_MAP = {
    "intent": CRM_INTENT,
    "architecture": CRM_ARCHITECTURE,
    "ui_schema": CRM_UI,
    "api_schema": CRM_API,
    "db_schema": CRM_DB,
    "auth_schema": CRM_AUTH,
    "business_rules": CRM_BUSINESS_RULES,
}


def get_mock_response(stage: str, user_prompt: str = "") -> dict:
    """Return a deterministic mock response for the given stage.

    For unknown prompts, still returns the CRM mock data with the
    app_name adjusted to reflect the prompt.
    """
    data = copy.deepcopy(_MOCK_MAP.get(stage, {}))

    # Adjust app name for non-CRM prompts
    if user_prompt and "crm" not in user_prompt.lower():
        if "app_name" in data:
            # Derive a name from the first few words of the prompt
            words = user_prompt.lower().split()[:3]
            data["app_name"] = "_".join(w for w in words if w.isalnum())[:30] or "custom_app"
        if "raw_prompt" in data:
            data["raw_prompt"] = user_prompt

    return data
