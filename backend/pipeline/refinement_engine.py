"""Stage 4: Refinement Engine — validates and repairs generated schemas."""

import time
from schemas.ui_schema import UISchema
from schemas.api_schema import APISchema
from schemas.db_schema import DBSchema
from schemas.auth_schema import AuthSchema
from schemas.business_rules_schema import BusinessRulesSchema
from schemas.final_app_spec_schema import ValidationIssue, RepairReport
from validators.cross_layer_validator import CrossLayerValidator
from validators.json_validator import SemanticValidator
from repair.repair_planner import RepairPlanner
from repair.targeted_regenerator import TargetedRegenerator
from config import settings


class RefinementEngine:
    """Runs validation → repair → re-validation cycles."""

    def __init__(self):
        self.cross_validator = CrossLayerValidator()
        self.semantic_validator = SemanticValidator()
        self.repair_planner = RepairPlanner()
        self.regenerator = TargetedRegenerator()

    def refine(self, schemas: dict) -> tuple[dict, RepairReport, int]:
        """Run refinement cycles. Returns (refined_schemas, report, duration_ms)."""
        start = time.time()
        all_issues: list[ValidationIssue] = []
        total_repaired = 0
        cycles = 0

        for cycle in range(settings.max_repair_cycles):
            cycles += 1
            # Run cross-layer validation
            issues = self.cross_validator.validate(
                schemas["ui"], schemas["api"], schemas["db"],
                schemas["auth"], schemas["business_rules"]
            )
            # Run semantic validation
            spec_dict = {k: v.model_dump() for k, v in schemas.items()}
            issues.extend(self.semantic_validator.validate(spec_dict))

            if not issues:
                break

            all_issues.extend(issues)

            # Plan repairs
            actions = self.repair_planner.plan(issues)
            if not actions:
                break

            # Apply targeted repairs
            schemas, repaired = self.regenerator.apply_repairs(schemas, actions)
            total_repaired += len(repaired)

        report = RepairReport(
            total_issues_found=len(all_issues),
            total_issues_repaired=total_repaired,
            repair_cycles=cycles,
            issues=all_issues,
        )
        duration = int((time.time() - start) * 1000)
        return schemas, report, duration
