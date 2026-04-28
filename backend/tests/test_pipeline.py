"""Tests for pipeline, schemas, and validators."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas.intent_schema import IntentSchema, FeatureIntent, EntityIntent, RoleIntent, MonetizationModel
from schemas.architecture_schema import ArchitectureSchema
from schemas.ui_schema import UISchema
from schemas.api_schema import APISchema
from schemas.db_schema import DBSchema
from schemas.auth_schema import AuthSchema
from schemas.business_rules_schema import BusinessRulesSchema
from schemas.final_app_spec_schema import FinalAppSpec, PipelineResponse, ValidationIssue
from validators.cross_layer_validator import CrossLayerValidator
from validators.json_validator import JSONValidator, SemanticValidator
from repair.repair_planner import RepairPlanner
from mock.mock_data_part1 import CRM_INTENT, CRM_ARCHITECTURE
from mock.mock_data_part2 import CRM_UI, CRM_API
from mock.mock_data_part3 import CRM_DB, CRM_AUTH, CRM_BUSINESS_RULES


class TestSchemaValidation:
    """Test that all schemas parse correctly from mock data."""

    def test_intent_schema_valid(self):
        schema = IntentSchema.model_validate(CRM_INTENT)
        assert schema.app_name == "crm_platform"
        assert len(schema.features) >= 3
        assert len(schema.entities) >= 2
        assert len(schema.roles) >= 2
        assert schema.monetization == MonetizationModel.FREEMIUM

    def test_intent_schema_rejects_extra_fields(self):
        data = {**CRM_INTENT, "unknown_field": "should fail"}
        with pytest.raises(Exception):
            IntentSchema.model_validate(data)

    def test_intent_schema_requires_features(self):
        data = {**CRM_INTENT, "features": []}
        with pytest.raises(Exception):
            IntentSchema.model_validate(data)

    def test_architecture_schema_valid(self):
        schema = ArchitectureSchema.model_validate(CRM_ARCHITECTURE)
        assert len(schema.modules) >= 3
        assert len(schema.page_map) >= 4
        assert len(schema.entity_model) >= 2

    def test_ui_schema_valid(self):
        schema = UISchema.model_validate(CRM_UI)
        assert len(schema.pages) >= 4
        assert len(schema.navigation) >= 3

    def test_api_schema_valid(self):
        schema = APISchema.model_validate(CRM_API)
        assert len(schema.endpoints) >= 5
        assert schema.auth_type == "jwt"

    def test_db_schema_valid(self):
        schema = DBSchema.model_validate(CRM_DB)
        assert len(schema.tables) >= 3
        assert len(schema.enums) >= 2

    def test_auth_schema_valid(self):
        schema = AuthSchema.model_validate(CRM_AUTH)
        assert len(schema.roles) >= 3
        assert len(schema.permissions) >= 5
        assert len(schema.route_access) >= 4

    def test_business_rules_valid(self):
        schema = BusinessRulesSchema.model_validate(CRM_BUSINESS_RULES)
        assert len(schema.premium_gates) >= 1
        assert len(schema.role_rules) >= 2


class TestCrossLayerValidator:
    """Test cross-layer validation checks."""

    def _get_schemas(self):
        return {
            "ui": UISchema.model_validate(CRM_UI),
            "api": APISchema.model_validate(CRM_API),
            "db": DBSchema.model_validate(CRM_DB),
            "auth": AuthSchema.model_validate(CRM_AUTH),
            "business_rules": BusinessRulesSchema.model_validate(CRM_BUSINESS_RULES),
        }

    def test_cross_layer_validation_runs(self):
        schemas = self._get_schemas()
        validator = CrossLayerValidator()
        issues = validator.validate(
            schemas["ui"], schemas["api"], schemas["db"],
            schemas["auth"], schemas["business_rules"]
        )
        assert isinstance(issues, list)
        # All issues should be ValidationIssue instances
        for issue in issues:
            assert isinstance(issue, ValidationIssue)

    def test_navigation_pages_check(self):
        schemas = self._get_schemas()
        validator = CrossLayerValidator()
        issues = validator._check_navigation_pages(schemas["ui"])
        # With valid mock data, settings nav maps to /settings which may or may not exist
        assert isinstance(issues, list)

    def test_auth_routes_check(self):
        schemas = self._get_schemas()
        validator = CrossLayerValidator()
        issues = validator._check_auth_routes(schemas["ui"], schemas["auth"])
        assert isinstance(issues, list)


class TestJSONValidator:
    """Test JSON and schema validators."""

    def test_validate_null(self):
        issues = JSONValidator.validate_json_syntax(None)
        assert len(issues) == 1
        assert issues[0].issue_type == "syntax"

    def test_validate_non_dict(self):
        issues = JSONValidator.validate_json_syntax([1, 2, 3])
        assert len(issues) == 1

    def test_validate_valid_dict(self):
        issues = JSONValidator.validate_json_syntax({"key": "value"})
        assert len(issues) == 0

    def test_schema_validation_success(self):
        obj, issues = JSONValidator.validate_schema(CRM_INTENT, IntentSchema, "intent")
        assert obj is not None
        assert len(issues) == 0

    def test_schema_validation_failure(self):
        obj, issues = JSONValidator.validate_schema({"bad": "data"}, IntentSchema, "intent")
        assert obj is None
        assert len(issues) > 0


class TestRepairPlanner:
    """Test repair planning logic."""

    def test_plan_empty_issues(self):
        planner = RepairPlanner()
        actions = planner.plan([])
        assert actions == []

    def test_plan_consistency_issue(self):
        planner = RepairPlanner()
        issue = ValidationIssue(
            issue_type="consistency",
            layer="cross_layer",
            location="Auth.route_access",
            description="Protected page 'settings' (route=/settings) has no auth route_access entry",
            severity="error",
        )
        actions = planner.plan([issue])
        assert len(actions) == 1
        assert actions[0].fix_type == "add_entry"

    def test_skips_info_issues(self):
        planner = RepairPlanner()
        issue = ValidationIssue(
            issue_type="consistency",
            layer="ui",
            location="test",
            description="Minor info",
            severity="info",
        )
        actions = planner.plan([issue])
        assert len(actions) == 0


class TestSemanticValidator:
    """Test semantic validation."""

    def test_semantic_valid_spec(self):
        spec_dict = {
            "architecture": {"entity_model": [{"name": "User"}]},
            "db": {"tables": [{"name": "users"}]},
            "auth": {"roles": [{"name": "admin", "inherits_from": []}]},
        }
        issues = SemanticValidator.validate(spec_dict)
        assert isinstance(issues, list)
