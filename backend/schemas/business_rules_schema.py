"""Business rules schema — Stage 3 sub-output.

Defines premium gating, role-based rules, workflows, and constraints.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


class PremiumGate(BaseModel):
    """A premium/paywall gate definition."""
    feature: str = Field(..., description="Feature being gated")
    gate_type: str = Field(default="hard", description="hard | soft | trial")
    required_plan: str = Field(default="premium")
    fallback_behavior: str = Field(default="show_upgrade_prompt")


class RoleRule(BaseModel):
    """A role-based business rule."""
    name: str
    description: str
    role: str = Field(..., description="Role this rule applies to")
    condition: str = Field(..., description="When this rule triggers")
    action: str = Field(..., description="What happens when triggered")
    priority: int = Field(default=0)


class WorkflowStep(BaseModel):
    """A step in a business workflow."""
    order: int
    name: str
    description: str
    actor: str = Field(..., description="Role performing this step")
    action: str
    next_step: Optional[str] = None
    condition: Optional[str] = None


class Workflow(BaseModel):
    """A business workflow definition."""
    name: str
    description: str
    trigger: str = Field(..., description="What triggers this workflow")
    steps: list[WorkflowStep] = Field(..., min_length=1)


class BusinessConstraint(BaseModel):
    """A business constraint or invariant."""
    name: str
    description: str
    type: str = Field(default="validation", description="validation | limit | dependency")
    scope: str = Field(..., description="Module or entity this applies to")
    rule: str = Field(..., description="The actual constraint rule")


class BusinessRulesSchema(BaseModel):
    """Complete business rules configuration."""

    model_config = {"extra": "forbid"}

    premium_gates: list[PremiumGate] = Field(default_factory=list)
    role_rules: list[RoleRule] = Field(default_factory=list)
    workflows: list[Workflow] = Field(default_factory=list)
    constraints: list[BusinessConstraint] = Field(default_factory=list)
