"""Cross-layer validator — checks consistency across UI, API, DB, Auth, Business Rules."""

from schemas.ui_schema import UISchema
from schemas.api_schema import APISchema
from schemas.db_schema import DBSchema
from schemas.auth_schema import AuthSchema
from schemas.business_rules_schema import BusinessRulesSchema
from schemas.final_app_spec_schema import ValidationIssue


class CrossLayerValidator:
    """Validates consistency across all generated schemas."""

    def validate(
        self, ui: UISchema, api: APISchema, db: DBSchema,
        auth: AuthSchema, biz: BusinessRulesSchema
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        issues.extend(self._check_ui_api_mapping(ui, api))
        issues.extend(self._check_api_db_mapping(api, db))
        issues.extend(self._check_auth_routes(ui, auth))
        issues.extend(self._check_permissions_roles(auth))
        issues.extend(self._check_premium_consistency(ui, api, biz))
        issues.extend(self._check_navigation_pages(ui))
        return issues

    def _check_ui_api_mapping(self, ui: UISchema, api: APISchema) -> list[ValidationIssue]:
        """Every UI form field should map to an API request field."""
        issues = []
        api_fields_by_endpoint: dict[str, set[str]] = {}
        for ep in api.endpoints:
            if ep.request:
                api_fields_by_endpoint[ep.path] = {f.name for f in ep.request.fields}

        for page in ui.pages:
            for comp in page.components:
                if comp.type.value == "form" and comp.data_source:
                    api_fields = set()
                    for path, fields in api_fields_by_endpoint.items():
                        if path in (comp.data_source or ""):
                            api_fields = fields
                            break
                    for field in comp.fields:
                        if api_fields and field.name not in api_fields:
                            issues.append(ValidationIssue(
                                issue_type="consistency",
                                layer="cross_layer",
                                location=f"UI.{page.name}.{comp.id}.{field.name}",
                                description=f"Form field '{field.name}' has no matching API request field in {comp.data_source}",
                                severity="warning",
                            ))
        return issues

    def _check_api_db_mapping(self, api: APISchema, db: DBSchema) -> list[ValidationIssue]:
        """Every API endpoint with related_entity should have a DB table."""
        issues = []
        table_names = {t.name.lower() for t in db.tables}
        for ep in api.endpoints:
            if ep.related_entity:
                entity_lower = ep.related_entity.lower()
                # Check both singular and plural
                if entity_lower not in table_names and f"{entity_lower}s" not in table_names:
                    issues.append(ValidationIssue(
                        issue_type="consistency",
                        layer="cross_layer",
                        location=f"API.{ep.name}",
                        description=f"Endpoint references entity '{ep.related_entity}' but no matching DB table found",
                        severity="error",
                    ))
        return issues

    def _check_auth_routes(self, ui: UISchema, auth: AuthSchema) -> list[ValidationIssue]:
        """Every protected UI page should have an auth route_access entry."""
        issues = []
        auth_routes = {ra.route for ra in auth.route_access}
        for page in ui.pages:
            if page.requires_auth and page.route not in auth_routes:
                issues.append(ValidationIssue(
                    issue_type="consistency",
                    layer="cross_layer",
                    location=f"Auth.route_access",
                    description=f"Protected page '{page.name}' (route={page.route}) has no auth route_access entry",
                    severity="error",
                ))
        return issues

    def _check_permissions_roles(self, auth: AuthSchema) -> list[ValidationIssue]:
        """All permission names referenced by roles must be defined."""
        issues = []
        defined_perms = {p.name for p in auth.permissions}
        for role in auth.roles:
            for perm in role.permissions:
                if perm not in defined_perms:
                    issues.append(ValidationIssue(
                        issue_type="consistency",
                        layer="auth",
                        location=f"Auth.roles.{role.name}",
                        description=f"Role '{role.name}' references undefined permission '{perm}'",
                        severity="error",
                    ))
        return issues

    def _check_premium_consistency(
        self, ui: UISchema, api: APISchema, biz: BusinessRulesSchema
    ) -> list[ValidationIssue]:
        """Premium-only features must be marked consistently."""
        issues = []
        premium_features = {g.feature for g in biz.premium_gates}
        # Check UI components marked premium have API endpoints also marked
        for page in ui.pages:
            for comp in page.components:
                if comp.premium_only and comp.data_source:
                    matching_eps = [e for e in api.endpoints if e.path == comp.data_source]
                    for ep in matching_eps:
                        if not ep.premium_only:
                            issues.append(ValidationIssue(
                                issue_type="consistency",
                                layer="cross_layer",
                                location=f"API.{ep.name}",
                                description=f"UI component '{comp.id}' is premium_only but API endpoint is not",
                                severity="warning",
                            ))
        return issues

    def _check_navigation_pages(self, ui: UISchema) -> list[ValidationIssue]:
        """Navigation routes must correspond to actual pages."""
        issues = []
        page_routes = {p.route for p in ui.pages}
        for nav in ui.navigation:
            if nav.route not in page_routes:
                issues.append(ValidationIssue(
                    issue_type="consistency",
                    layer="ui",
                    location=f"UI.navigation.{nav.label}",
                    description=f"Navigation item '{nav.label}' points to route '{nav.route}' which has no page",
                    severity="error",
                ))
        return issues
