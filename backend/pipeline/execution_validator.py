"""Stage 5: Execution Validator — verifies the final spec is executable."""

import time
from schemas.final_app_spec_schema import FinalAppSpec, ExecutionResult


class ExecutionValidator:
    """Validates that the final app spec can drive a runtime."""

    def validate(self, spec: FinalAppSpec) -> tuple[ExecutionResult, int]:
        """Run execution readiness checks. Returns (result, duration_ms)."""
        start = time.time()
        details = []
        checks = {
            "routes_valid": self._check_routes(spec, details),
            "forms_api_mapped": self._check_forms_api(spec, details),
            "api_db_mapped": self._check_api_db(spec, details),
            "auth_coverage_complete": self._check_auth_coverage(spec, details),
            "business_rules_consistent": self._check_business_rules(spec, details),
        }

        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        score = passed / total if total > 0 else 0.0

        result = ExecutionResult(
            is_executable=score >= 0.8,
            routes_valid=checks["routes_valid"],
            forms_api_mapped=checks["forms_api_mapped"],
            api_db_mapped=checks["api_db_mapped"],
            auth_coverage_complete=checks["auth_coverage_complete"],
            business_rules_consistent=checks["business_rules_consistent"],
            details=details,
            score=round(score, 2),
        )
        duration = int((time.time() - start) * 1000)
        return result, duration

    def _check_routes(self, spec: FinalAppSpec, details: list[str]) -> bool:
        """All navigation routes must point to existing pages."""
        page_routes = {p.route for p in spec.ui.pages}
        nav_routes = {n.route for n in spec.ui.navigation}
        missing = nav_routes - page_routes
        if missing:
            details.append(f"❌ Routes without pages: {missing}")
            return False
        details.append(f"✅ All {len(nav_routes)} navigation routes map to pages")
        return True

    def _check_forms_api(self, spec: FinalAppSpec, details: list[str]) -> bool:
        """Form components should have corresponding API endpoints."""
        form_count = 0
        mapped = 0
        api_paths = {e.path for e in spec.api.endpoints}
        for page in spec.ui.pages:
            for comp in page.components:
                if comp.type.value == "form":
                    form_count += 1
                    if comp.data_source and any(comp.data_source in p for p in api_paths):
                        mapped += 1
        if form_count == 0:
            details.append("✅ No forms to validate")
            return True
        ratio = mapped / form_count
        details.append(f"{'✅' if ratio >= 0.7 else '❌'} Forms→API mapping: {mapped}/{form_count} ({ratio:.0%})")
        return ratio >= 0.7

    def _check_api_db(self, spec: FinalAppSpec, details: list[str]) -> bool:
        """API endpoints with entities should have DB tables."""
        table_names = {t.name.lower() for t in spec.db.tables}
        entity_eps = [e for e in spec.api.endpoints if e.related_entity]
        if not entity_eps:
            details.append("✅ No entity-bound endpoints")
            return True
        mapped = 0
        for ep in entity_eps:
            e = ep.related_entity.lower()
            if e in table_names or f"{e}s" in table_names:
                mapped += 1
        ratio = mapped / len(entity_eps)
        details.append(f"{'✅' if ratio >= 0.8 else '❌'} API→DB mapping: {mapped}/{len(entity_eps)} ({ratio:.0%})")
        return ratio >= 0.8

    def _check_auth_coverage(self, spec: FinalAppSpec, details: list[str]) -> bool:
        """Protected pages must have route_access entries."""
        protected = [p for p in spec.ui.pages if p.requires_auth]
        auth_routes = {r.route for r in spec.auth.route_access}
        covered = sum(1 for p in protected if p.route in auth_routes)
        if not protected:
            details.append("✅ No protected pages")
            return True
        ratio = covered / len(protected)
        details.append(f"{'✅' if ratio >= 0.8 else '❌'} Auth coverage: {covered}/{len(protected)} ({ratio:.0%})")
        return ratio >= 0.8

    def _check_business_rules(self, spec: FinalAppSpec, details: list[str]) -> bool:
        """Business rules should reference known roles and entities."""
        role_names = {r.name for r in spec.auth.roles}
        issues = 0
        for rule in spec.business_rules.role_rules:
            if rule.role not in role_names:
                issues += 1
        if issues:
            details.append(f"❌ {issues} business rules reference unknown roles")
            return False
        details.append(f"✅ All business rules reference valid roles")
        return True
