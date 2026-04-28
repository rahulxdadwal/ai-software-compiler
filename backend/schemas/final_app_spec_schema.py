"""Final App Spec schema — composite output of the entire pipeline.

This is the single deliverable that the pipeline produces.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from schemas.intent_schema import IntentSchema
from schemas.architecture_schema import ArchitectureSchema
from schemas.ui_schema import UISchema
from schemas.api_schema import APISchema
from schemas.db_schema import DBSchema
from schemas.auth_schema import AuthSchema
from schemas.business_rules_schema import BusinessRulesSchema


class ValidationIssue(BaseModel):
    """A validation issue found during refinement."""
    issue_type: str = Field(..., description="syntax | schema | consistency | semantic")
    layer: str = Field(..., description="ui | api | db | auth | business_rules | cross_layer")
    location: str = Field(..., description="Where in the spec the issue was found")
    description: str
    severity: str = Field(default="error", description="error | warning | info")
    repaired: bool = Field(default=False)
    repair_action: Optional[str] = None


class RepairReport(BaseModel):
    """Report of all repairs performed during refinement."""
    total_issues_found: int = Field(default=0)
    total_issues_repaired: int = Field(default=0)
    repair_cycles: int = Field(default=0)
    issues: list[ValidationIssue] = Field(default_factory=list)


class ExecutionResult(BaseModel):
    """Result of execution readiness validation."""
    is_executable: bool = Field(default=False)
    routes_valid: bool = Field(default=False)
    forms_api_mapped: bool = Field(default=False)
    api_db_mapped: bool = Field(default=False)
    auth_coverage_complete: bool = Field(default=False)
    business_rules_consistent: bool = Field(default=False)
    details: list[str] = Field(default_factory=list)
    score: float = Field(default=0.0, description="0.0 to 1.0 execution readiness score")


class PipelineMetadata(BaseModel):
    """Metadata about the pipeline execution."""
    pipeline_version: str = Field(default="1.0.0")
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    total_duration_ms: int = Field(default=0)
    stage_durations_ms: dict[str, int] = Field(default_factory=dict)
    mock_mode: bool = Field(default=False)
    assumptions: list[str] = Field(default_factory=list)
    ambiguities_detected: int = Field(default=0)


class StageOutput(BaseModel):
    """Output of a single pipeline stage for the frontend."""
    stage_name: str
    status: str = Field(default="pending", description="pending | running | completed | failed")
    duration_ms: int = Field(default=0)
    data: Optional[dict] = None
    error: Optional[str] = None


class FinalAppSpec(BaseModel):
    """The complete compiled application specification."""

    model_config = {"extra": "forbid"}

    intent: IntentSchema
    architecture: ArchitectureSchema
    ui: UISchema
    api: APISchema
    db: DBSchema
    auth: AuthSchema
    business_rules: BusinessRulesSchema
    validation_report: RepairReport = Field(default_factory=RepairReport)
    execution_result: ExecutionResult = Field(default_factory=ExecutionResult)
    metadata: PipelineMetadata = Field(default_factory=PipelineMetadata)


class PipelineResponse(BaseModel):
    """Full pipeline response sent to the frontend."""
    success: bool
    app_spec: Optional[FinalAppSpec] = None
    stages: list[StageOutput] = Field(default_factory=list)
    error: Optional[str] = None
