"""Intent schema — Stage 1 output.

Captures the structured interpretation of a raw natural-language product prompt.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class MonetizationModel(str, Enum):
    FREE = "free"
    FREEMIUM = "freemium"
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    USAGE_BASED = "usage_based"


class FeatureIntent(BaseModel):
    """A single feature extracted from the prompt."""
    name: str = Field(..., description="Feature name, e.g. 'contacts_management'")
    description: str = Field(..., description="What this feature does")
    priority: str = Field(default="core", description="core | nice_to_have | premium")
    requires_auth: bool = Field(default=False)
    premium_only: bool = Field(default=False)


class EntityIntent(BaseModel):
    """A data entity identified in the prompt."""
    name: str = Field(..., description="Entity name, e.g. 'Contact'")
    attributes: list[str] = Field(default_factory=list, description="Known attributes")
    relations: list[str] = Field(default_factory=list, description="Related entity names")


class RoleIntent(BaseModel):
    """A user role identified in the prompt."""
    name: str = Field(..., description="Role name, e.g. 'admin'")
    permissions: list[str] = Field(default_factory=list, description="High-level permissions")
    is_default: bool = Field(default=False)


class ActionIntent(BaseModel):
    """A user action or workflow step."""
    name: str = Field(..., description="Action name, e.g. 'create_contact'")
    actor: str = Field(..., description="Role that performs this action")
    target_entity: Optional[str] = Field(default=None)
    requires_premium: bool = Field(default=False)


class Ambiguity(BaseModel):
    """An ambiguity or gap detected in the prompt."""
    area: str = Field(..., description="Where the ambiguity lies")
    description: str = Field(..., description="What is unclear")
    assumption: str = Field(..., description="Assumption made to proceed")


class IntentSchema(BaseModel):
    """Complete Stage 1 output — structured intent from raw prompt."""

    model_config = {"extra": "forbid"}

    raw_prompt: str = Field(..., description="Original user prompt")
    app_name: str = Field(..., description="Inferred application name")
    app_description: str = Field(..., description="Brief app description")
    features: list[FeatureIntent] = Field(..., min_length=1)
    entities: list[EntityIntent] = Field(..., min_length=1)
    roles: list[RoleIntent] = Field(..., min_length=1)
    actions: list[ActionIntent] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list, description="Business constraints")
    monetization: MonetizationModel = Field(default=MonetizationModel.FREE)
    ambiguities: list[Ambiguity] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list, description="Explicit assumptions made")
