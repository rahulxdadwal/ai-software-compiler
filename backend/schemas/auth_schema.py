"""Auth schema — Stage 3 sub-output.

Defines roles, permissions, and route access control.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


class Permission(BaseModel):
    """A permission that can be assigned to roles."""
    name: str = Field(..., description="Permission identifier, e.g. 'contacts:read'")
    description: str = Field(default="")
    resource: str = Field(..., description="Resource this permission applies to")
    action: str = Field(..., description="read | write | delete | manage")


class Role(BaseModel):
    """A role definition with permissions."""
    name: str
    display_name: str
    level: int = Field(..., description="Hierarchy level, 0 = superadmin")
    permissions: list[str] = Field(..., description="List of permission names")
    is_default: bool = Field(default=False)
    description: Optional[str] = None


class RouteAccess(BaseModel):
    """Access control rule for a specific route."""
    route: str = Field(..., description="Route path, e.g. '/dashboard'")
    allowed_roles: list[str] = Field(..., min_length=1)
    requires_auth: bool = Field(default=True)
    premium_only: bool = Field(default=False)


class AuthSchema(BaseModel):
    """Complete authentication and authorization schema."""

    model_config = {"extra": "forbid"}

    auth_type: str = Field(default="jwt")
    roles: list[Role] = Field(..., min_length=1)
    permissions: list[Permission] = Field(default_factory=list)
    route_access: list[RouteAccess] = Field(default_factory=list)
    token_expiry_minutes: int = Field(default=60)
    refresh_enabled: bool = Field(default=True)
