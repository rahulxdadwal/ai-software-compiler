"""Architecture schema — Stage 2 output.

Converts intent into a system-level architecture plan.
"""

from __future__ import annotations
from pydantic import BaseModel, Field


class AppModule(BaseModel):
    """A logical module of the application."""
    name: str = Field(..., description="Module name, e.g. 'auth', 'contacts'")
    description: str
    features: list[str] = Field(..., description="Feature names belonging to this module")
    entities: list[str] = Field(..., description="Entity names owned by this module")


class PageDefinition(BaseModel):
    """A page in the application."""
    name: str = Field(..., description="Page identifier, e.g. 'dashboard'")
    route: str = Field(..., description="URL route, e.g. '/dashboard'")
    module: str = Field(..., description="Owning module name")
    requires_auth: bool = Field(default=False)
    allowed_roles: list[str] = Field(default_factory=list)
    description: str = Field(default="")


class EntityModel(BaseModel):
    """An entity in the data model with its attributes."""
    name: str
    attributes: list[dict] = Field(..., description="List of {name, type, required, unique} dicts")
    relations: list[dict] = Field(default_factory=list, description="List of {target, type, field} dicts")


class RoleModel(BaseModel):
    """Role definition in the architecture."""
    name: str
    level: int = Field(..., description="Hierarchy level (0 = highest)")
    inherits_from: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)


class UserFlow(BaseModel):
    """A user workflow or journey."""
    name: str
    actor: str = Field(..., description="Role performing this flow")
    steps: list[str] = Field(..., description="Ordered list of step descriptions")
    pages_involved: list[str] = Field(default_factory=list)


class ArchitectureSchema(BaseModel):
    """Complete Stage 2 output — system architecture plan."""

    model_config = {"extra": "forbid"}

    app_name: str
    modules: list[AppModule] = Field(..., min_length=1)
    page_map: list[PageDefinition] = Field(..., min_length=1)
    entity_model: list[EntityModel] = Field(..., min_length=1)
    role_model: list[RoleModel] = Field(..., min_length=1)
    feature_map: dict[str, list[str]] = Field(
        ..., description="Module name → list of feature names"
    )
    flows: list[UserFlow] = Field(default_factory=list)
    tech_decisions: list[str] = Field(
        default_factory=list, description="Key technical decisions"
    )
