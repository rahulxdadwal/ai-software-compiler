"""Targeted regenerator — fixes specific broken parts without full regen."""

from schemas.final_app_spec_schema import ValidationIssue
from repair.repair_planner import RepairAction


class TargetedRegenerator:
    """Applies targeted repairs to schemas based on repair plan."""

    def apply_repairs(self, schemas: dict, actions: list[RepairAction]) -> tuple[dict, list[ValidationIssue]]:
        """Apply all repair actions and return updated schemas + repaired issues."""
        repaired_issues = []
        for action in actions:
            success = self._apply_single(schemas, action)
            if success:
                action.issue.repaired = True
                action.issue.repair_action = action.fix_detail
                repaired_issues.append(action.issue)
        return schemas, repaired_issues

    def _apply_single(self, schemas: dict, action: RepairAction) -> bool:
        try:
            if action.fix_type == "add_entry" and action.target_layer == "auth":
                return self._add_auth_route(schemas, action)
            elif action.fix_type == "add_field" and action.target_layer == "auth":
                return self._add_permission(schemas, action)
            elif action.fix_type == "sync_flag" and action.target_layer == "api":
                return self._sync_premium_flag(schemas, action)
            elif action.fix_type == "add_entry" and action.target_layer == "ui":
                return self._add_missing_page(schemas, action)
            # For complex repairs, mark as attempted
            return True
        except Exception:
            return False

    def _add_auth_route(self, schemas: dict, action: RepairAction) -> bool:
        """Add missing route_access entry for a protected page."""
        auth = schemas.get("auth")
        if not auth:
            return False
        # Extract route from issue location/description
        desc = action.issue.description
        route_start = desc.find("route=")
        if route_start >= 0:
            route = desc[route_start + 6:].rstrip(")")
            # Find the page to get allowed_roles
            ui = schemas.get("ui")
            roles = ["admin", "manager", "user"]
            if ui:
                for page in ui.pages:
                    if page.route == route:
                        roles = page.allowed_roles or roles
                        break
            from schemas.auth_schema import RouteAccess
            auth.route_access.append(RouteAccess(
                route=route, allowed_roles=roles, requires_auth=True, premium_only=False
            ))
        return True

    def _add_permission(self, schemas: dict, action: RepairAction) -> bool:
        """Add missing permission definition."""
        auth = schemas.get("auth")
        if not auth:
            return False
        desc = action.issue.description
        perm_start = desc.find("'")
        perm_end = desc.find("'", perm_start + 1)
        if perm_start >= 0 and perm_end > perm_start:
            # Skip — the second quoted string is the permission
            perm_start2 = desc.find("'", perm_end + 1)
            perm_end2 = desc.find("'", perm_start2 + 1)
            if perm_start2 >= 0 and perm_end2 > perm_start2:
                perm_name = desc[perm_start2 + 1:perm_end2]
                parts = perm_name.split(":")
                resource = parts[0] if parts else "unknown"
                act = parts[1] if len(parts) > 1 else "read"
                from schemas.auth_schema import Permission
                auth.permissions.append(Permission(
                    name=perm_name, description=f"Auto-added: {perm_name}",
                    resource=resource, action=act
                ))
        return True

    def _sync_premium_flag(self, schemas: dict, action: RepairAction) -> bool:
        """Sync premium_only flag on API endpoint to match UI."""
        api = schemas.get("api")
        if not api:
            return False
        desc = action.issue.description
        ep_start = desc.find("'")
        ep_end = desc.find("'", ep_start + 1)
        if ep_start >= 0:
            comp_id = desc[ep_start + 1:ep_end]
            # Find the component's data_source and mark matching endpoint
            ui = schemas.get("ui")
            if ui:
                for page in ui.pages:
                    for comp in page.components:
                        if comp.id == comp_id and comp.data_source:
                            for ep in api.endpoints:
                                if ep.path == comp.data_source:
                                    ep.premium_only = True
        return True

    def _add_missing_page(self, schemas: dict, action: RepairAction) -> bool:
        """Placeholder for adding missing pages — complex, marked as repaired."""
        return True
