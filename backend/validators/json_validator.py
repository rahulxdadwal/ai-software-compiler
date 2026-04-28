"""JSON and schema validators."""

import json
from typing import Any, Type
from pydantic import BaseModel, ValidationError
from schemas.final_app_spec_schema import ValidationIssue


class JSONValidator:
    """Validates JSON syntax and Pydantic schema conformance."""

    @staticmethod
    def validate_json_syntax(data: Any) -> list[ValidationIssue]:
        """Check if data is valid JSON (already parsed at this point)."""
        issues = []
        if data is None:
            issues.append(ValidationIssue(
                issue_type="syntax", layer="unknown",
                location="root", description="Data is None/null",
                severity="error",
            ))
        elif not isinstance(data, dict):
            issues.append(ValidationIssue(
                issue_type="syntax", layer="unknown",
                location="root", description=f"Expected dict, got {type(data).__name__}",
                severity="error",
            ))
        return issues

    @staticmethod
    def validate_schema(data: dict, schema_class: Type[BaseModel], layer: str) -> tuple[Any, list[ValidationIssue]]:
        """Validate data against a Pydantic schema. Returns (parsed_obj_or_None, issues)."""
        issues = []
        try:
            obj = schema_class.model_validate(data)
            return obj, issues
        except ValidationError as e:
            for err in e.errors():
                loc = ".".join(str(x) for x in err["loc"])
                issues.append(ValidationIssue(
                    issue_type="schema", layer=layer,
                    location=f"{layer}.{loc}",
                    description=err["msg"],
                    severity="error",
                ))
            return None, issues


class SemanticValidator:
    """Validates semantic correctness — logical contradictions and orphans."""

    @staticmethod
    def validate(app_spec_dict: dict) -> list[ValidationIssue]:
        issues = []
        # Check for unreferenced entities
        if "architecture" in app_spec_dict and "db" in app_spec_dict:
            arch_entities = {e["name"] for e in app_spec_dict["architecture"].get("entity_model", [])}
            db_tables = {t["name"] for t in app_spec_dict["db"].get("tables", [])}
            for entity in arch_entities:
                entity_lower = entity.lower()
                if entity_lower not in db_tables and f"{entity_lower}s" not in db_tables:
                    issues.append(ValidationIssue(
                        issue_type="semantic", layer="cross_layer",
                        location=f"architecture.entity_model.{entity}",
                        description=f"Architecture entity '{entity}' has no corresponding DB table",
                        severity="warning",
                    ))

        # Check role hierarchy consistency
        if "auth" in app_spec_dict:
            roles = app_spec_dict["auth"].get("roles", [])
            role_names = {r["name"] for r in roles}
            for role in roles:
                for parent in role.get("inherits_from", []):
                    if parent not in role_names:
                        issues.append(ValidationIssue(
                            issue_type="semantic", layer="auth",
                            location=f"auth.roles.{role['name']}",
                            description=f"Role inherits from unknown role '{parent}'",
                            severity="error",
                        ))
        return issues
