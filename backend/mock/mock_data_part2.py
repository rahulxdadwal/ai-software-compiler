"""Mock schema responses for CRM demo prompt — Part 2."""

CRM_UI = {
    "pages": [
        {"name": "login", "route": "/login", "title": "Login", "layout": "single_column", "components": [
            {"id": "login_form", "type": "form", "title": "Sign In", "fields": [
                {"name": "email", "label": "Email", "field_type": "email", "required": True, "validation": "valid email format", "options": []},
                {"name": "password", "label": "Password", "field_type": "password", "required": True, "validation": "min 8 characters", "options": []}
            ], "columns": [], "data_source": None, "actions": ["login"], "premium_only": False}
        ], "requires_auth": False, "allowed_roles": []},
        {"name": "register", "route": "/register", "title": "Register", "layout": "single_column", "components": [
            {"id": "register_form", "type": "form", "title": "Create Account", "fields": [
                {"name": "name", "label": "Full Name", "field_type": "text", "required": True, "validation": None, "options": []},
                {"name": "email", "label": "Email", "field_type": "email", "required": True, "validation": "valid email format", "options": []},
                {"name": "password", "label": "Password", "field_type": "password", "required": True, "validation": "min 8 characters", "options": []}
            ], "columns": [], "data_source": None, "actions": ["register"], "premium_only": False}
        ], "requires_auth": False, "allowed_roles": []},
        {"name": "dashboard", "route": "/dashboard", "title": "Dashboard", "layout": "dashboard_grid", "components": [
            {"id": "total_contacts_stat", "type": "stat", "title": "Total Contacts", "fields": [], "columns": [], "data_source": "/api/v1/contacts/stats", "actions": [], "premium_only": False},
            {"id": "recent_contacts", "type": "table", "title": "Recent Contacts", "fields": [], "columns": [
                {"key": "name", "label": "Name", "sortable": True, "filterable": True},
                {"key": "email", "label": "Email", "sortable": False, "filterable": True},
                {"key": "status", "label": "Status", "sortable": True, "filterable": True}
            ], "data_source": "/api/v1/contacts?limit=5&sort=-created_at", "actions": ["view"], "premium_only": False}
        ], "requires_auth": True, "allowed_roles": ["admin", "manager", "user"]},
        {"name": "contacts", "route": "/contacts", "title": "Contacts", "layout": "sidebar_main", "components": [
            {"id": "contacts_table", "type": "table", "title": "All Contacts", "fields": [], "columns": [
                {"key": "name", "label": "Name", "sortable": True, "filterable": True},
                {"key": "email", "label": "Email", "sortable": False, "filterable": True},
                {"key": "phone", "label": "Phone", "sortable": False, "filterable": False},
                {"key": "company", "label": "Company", "sortable": True, "filterable": True},
                {"key": "status", "label": "Status", "sortable": True, "filterable": True}
            ], "data_source": "/api/v1/contacts", "actions": ["create", "edit", "delete"], "premium_only": False},
            {"id": "create_contact_form", "type": "form", "title": "New Contact", "fields": [
                {"name": "name", "label": "Name", "field_type": "text", "required": True, "validation": None, "options": []},
                {"name": "email", "label": "Email", "field_type": "email", "required": False, "validation": "valid email", "options": []},
                {"name": "phone", "label": "Phone", "field_type": "text", "required": False, "validation": None, "options": []},
                {"name": "company", "label": "Company", "field_type": "text", "required": False, "validation": None, "options": []},
                {"name": "status", "label": "Status", "field_type": "select", "required": True, "validation": None, "options": ["lead", "active", "inactive"]}
            ], "columns": [], "data_source": "/api/v1/contacts", "actions": ["submit"], "premium_only": False}
        ], "requires_auth": True, "allowed_roles": ["admin", "manager", "user"]},
        {"name": "analytics", "route": "/analytics", "title": "Analytics", "layout": "dashboard_grid", "components": [
            {"id": "contacts_chart", "type": "chart", "title": "Contacts Over Time", "fields": [], "columns": [], "data_source": "/api/v1/analytics/contacts", "actions": [], "premium_only": True},
            {"id": "revenue_chart", "type": "chart", "title": "Revenue", "fields": [], "columns": [], "data_source": "/api/v1/analytics/revenue", "actions": [], "premium_only": True}
        ], "requires_auth": True, "allowed_roles": ["admin"]},
        {"name": "billing", "route": "/billing", "title": "Billing", "layout": "single_column", "components": [
            {"id": "plan_card", "type": "card", "title": "Current Plan", "fields": [], "columns": [], "data_source": "/api/v1/subscriptions/current", "actions": ["upgrade", "cancel"], "premium_only": False}
        ], "requires_auth": True, "allowed_roles": ["admin", "manager", "user"]}
    ],
    "navigation": [
        {"label": "Dashboard", "route": "/dashboard", "icon": "home", "visible_to": ["admin", "manager", "user"], "premium_only": False},
        {"label": "Contacts", "route": "/contacts", "icon": "users", "visible_to": ["admin", "manager", "user"], "premium_only": False},
        {"label": "Analytics", "route": "/analytics", "icon": "chart", "visible_to": ["admin"], "premium_only": True},
        {"label": "Billing", "route": "/billing", "icon": "credit-card", "visible_to": ["admin", "manager", "user"], "premium_only": False},
        {"label": "Settings", "route": "/settings", "icon": "settings", "visible_to": ["admin"], "premium_only": False}
    ],
    "theme": {"primary_color": "#6366f1", "mode": "light"}
}

CRM_API = {
    "base_url": "/api",
    "version": "v1",
    "endpoints": [
        {"path": "/api/v1/auth/login", "method": "POST", "name": "login", "description": "User login", "module": "auth", "requires_auth": False, "allowed_roles": [], "request": {"content_type": "application/json", "fields": [{"name": "email", "type": "email", "required": True, "description": "User email", "validation": "valid email", "enum_values": []}, {"name": "password", "type": "string", "required": True, "description": "User password", "validation": "min 8 chars", "enum_values": []}]}, "response": {"status_code": 200, "content_type": "application/json", "fields": [{"name": "token", "type": "string", "required": True, "description": "JWT token", "validation": None, "enum_values": []}, {"name": "user", "type": "object", "required": True, "description": "User object", "validation": None, "enum_values": []}], "is_list": False}, "rate_limited": True, "premium_only": False, "related_entity": "User"},
        {"path": "/api/v1/auth/register", "method": "POST", "name": "register", "description": "User registration", "module": "auth", "requires_auth": False, "allowed_roles": [], "request": {"content_type": "application/json", "fields": [{"name": "name", "type": "string", "required": True, "description": "Full name", "validation": None, "enum_values": []}, {"name": "email", "type": "email", "required": True, "description": "Email", "validation": "valid email", "enum_values": []}, {"name": "password", "type": "string", "required": True, "description": "Password", "validation": "min 8 chars", "enum_values": []}]}, "response": {"status_code": 201, "content_type": "application/json", "fields": [{"name": "id", "type": "string", "required": True, "description": "User ID", "validation": None, "enum_values": []}], "is_list": False}, "rate_limited": True, "premium_only": False, "related_entity": "User"},
        {"path": "/api/v1/contacts", "method": "GET", "name": "list_contacts", "description": "List contacts", "module": "contacts", "requires_auth": True, "allowed_roles": ["admin", "manager", "user"], "request": None, "response": {"status_code": 200, "content_type": "application/json", "fields": [{"name": "id", "type": "string", "required": True, "description": "Contact ID", "validation": None, "enum_values": []}, {"name": "name", "type": "string", "required": True, "description": "Name", "validation": None, "enum_values": []}, {"name": "email", "type": "email", "required": False, "description": "Email", "validation": None, "enum_values": []}, {"name": "phone", "type": "string", "required": False, "description": "Phone", "validation": None, "enum_values": []}, {"name": "company", "type": "string", "required": False, "description": "Company", "validation": None, "enum_values": []}, {"name": "status", "type": "string", "required": True, "description": "Status", "validation": None, "enum_values": ["lead", "active", "inactive"]}], "is_list": True}, "rate_limited": False, "premium_only": False, "related_entity": "Contact"},
        {"path": "/api/v1/contacts", "method": "POST", "name": "create_contact", "description": "Create contact", "module": "contacts", "requires_auth": True, "allowed_roles": ["admin", "manager", "user"], "request": {"content_type": "application/json", "fields": [{"name": "name", "type": "string", "required": True, "description": "Name", "validation": None, "enum_values": []}, {"name": "email", "type": "email", "required": False, "description": "Email", "validation": "valid email", "enum_values": []}, {"name": "phone", "type": "string", "required": False, "description": "Phone", "validation": None, "enum_values": []}, {"name": "company", "type": "string", "required": False, "description": "Company", "validation": None, "enum_values": []}, {"name": "status", "type": "string", "required": True, "description": "Status", "validation": None, "enum_values": ["lead", "active", "inactive"]}]}, "response": {"status_code": 201, "content_type": "application/json", "fields": [{"name": "id", "type": "string", "required": True, "description": "Created ID", "validation": None, "enum_values": []}], "is_list": False}, "rate_limited": False, "premium_only": False, "related_entity": "Contact"},
        {"path": "/api/v1/contacts/{id}", "method": "PUT", "name": "update_contact", "description": "Update contact", "module": "contacts", "requires_auth": True, "allowed_roles": ["admin", "manager", "user"], "request": {"content_type": "application/json", "fields": [{"name": "name", "type": "string", "required": False, "description": "Name", "validation": None, "enum_values": []}, {"name": "email", "type": "email", "required": False, "description": "Email", "validation": None, "enum_values": []}, {"name": "phone", "type": "string", "required": False, "description": "Phone", "validation": None, "enum_values": []}, {"name": "company", "type": "string", "required": False, "description": "Company", "validation": None, "enum_values": []}, {"name": "status", "type": "string", "required": False, "description": "Status", "validation": None, "enum_values": ["lead", "active", "inactive"]}]}, "response": {"status_code": 200, "content_type": "application/json", "fields": [{"name": "id", "type": "string", "required": True, "description": "Contact ID", "validation": None, "enum_values": []}], "is_list": False}, "rate_limited": False, "premium_only": False, "related_entity": "Contact"},
        {"path": "/api/v1/contacts/{id}", "method": "DELETE", "name": "delete_contact", "description": "Delete contact", "module": "contacts", "requires_auth": True, "allowed_roles": ["admin", "manager"], "request": None, "response": {"status_code": 204, "content_type": "application/json", "fields": [], "is_list": False}, "rate_limited": False, "premium_only": False, "related_entity": "Contact"},
        {"path": "/api/v1/analytics/contacts", "method": "GET", "name": "analytics_contacts", "description": "Contact analytics", "module": "analytics", "requires_auth": True, "allowed_roles": ["admin"], "request": None, "response": {"status_code": 200, "content_type": "application/json", "fields": [{"name": "data", "type": "array", "required": True, "description": "Chart data", "validation": None, "enum_values": []}], "is_list": False}, "rate_limited": False, "premium_only": True, "related_entity": None},
        {"path": "/api/v1/subscriptions/current", "method": "GET", "name": "get_subscription", "description": "Get current subscription", "module": "billing", "requires_auth": True, "allowed_roles": ["admin", "manager", "user"], "request": None, "response": {"status_code": 200, "content_type": "application/json", "fields": [{"name": "plan", "type": "string", "required": True, "description": "Plan name", "validation": None, "enum_values": ["free", "premium"]}, {"name": "status", "type": "string", "required": True, "description": "Status", "validation": None, "enum_values": ["active", "cancelled", "expired"]}], "is_list": False}, "rate_limited": False, "premium_only": False, "related_entity": "Subscription"},
        {"path": "/api/v1/contacts/stats", "method": "GET", "name": "contacts_stats", "description": "Contact statistics", "module": "contacts", "requires_auth": True, "allowed_roles": ["admin", "manager", "user"], "request": None, "response": {"status_code": 200, "content_type": "application/json", "fields": [{"name": "total", "type": "integer", "required": True, "description": "Total contacts", "validation": None, "enum_values": []}], "is_list": False}, "rate_limited": False, "premium_only": False, "related_entity": "Contact"}
    ],
    "auth_type": "jwt"
}
