"""Repair planner — analyzes validation issues and creates repair plans."""

from schemas.final_app_spec_schema import ValidationIssue


class RepairAction:
    """A single repair action to fix a validation issue."""
    def __init__(self, issue: ValidationIssue, target_layer: str, fix_type: str, fix_detail: str):
        self.issue = issue
        self.target_layer = target_layer
        self.fix_type = fix_type  # "add_field" | "fix_reference" | "sync_flag" | "add_entry"
        self.fix_detail = fix_detail


class RepairPlanner:
    """Analyzes validation issues and produces a repair plan."""

    def plan(self, issues: list[ValidationIssue]) -> list[RepairAction]:
        """Create repair actions for each fixable issue."""
        actions = []
        for issue in issues:
            if issue.severity == "info":
                continue
            action = self._plan_single(issue)
            if action:
                actions.append(action)
        return actions

    def _plan_single(self, issue: ValidationIssue) -> RepairAction | None:
        if issue.issue_type == "consistency":
            return self._plan_consistency_fix(issue)
        elif issue.issue_type == "schema":
            return RepairAction(issue, issue.layer, "fix_schema", f"Fix schema error at {issue.location}")
        elif issue.issue_type == "semantic":
            return RepairAction(issue, issue.layer, "fix_reference", f"Fix semantic issue: {issue.description}")
        return None

    def _plan_consistency_fix(self, issue: ValidationIssue) -> RepairAction:
        desc = issue.description.lower()
        if "no matching api request field" in desc:
            return RepairAction(issue, "api", "add_field", f"Add missing API field: {issue.description}")
        elif "no matching db table" in desc:
            return RepairAction(issue, "db", "add_entry", f"Add missing DB table: {issue.description}")
        elif "no auth route_access" in desc:
            return RepairAction(issue, "auth", "add_entry", f"Add route_access entry: {issue.description}")
        elif "undefined permission" in desc:
            return RepairAction(issue, "auth", "add_field", f"Add missing permission: {issue.description}")
        elif "premium_only but api endpoint is not" in desc:
            return RepairAction(issue, "api", "sync_flag", f"Sync premium flag: {issue.description}")
        elif "no page" in desc:
            return RepairAction(issue, "ui", "add_entry", f"Add missing page: {issue.description}")
        return RepairAction(issue, issue.layer, "manual", issue.description)
