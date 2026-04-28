"""Deterministic mock responses for demo mode."""

CRM_INTENT = {
    "raw_prompt": "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.",
    "app_name": "crm_platform",
    "app_description": "A customer relationship management platform with role-based access, premium features, and analytics.",
    "features": [
        {"name": "user_auth", "description": "User registration and login", "priority": "core", "requires_auth": False, "premium_only": False},
        {"name": "contacts_management", "description": "CRUD operations for contacts", "priority": "core", "requires_auth": True, "premium_only": False},
        {"name": "dashboard", "description": "Overview dashboard with key metrics", "priority": "core", "requires_auth": True, "premium_only": False},
        {"name": "analytics", "description": "Advanced analytics and reporting", "priority": "premium", "requires_auth": True, "premium_only": False},
        {"name": "payments", "description": "Premium plan subscription and payments", "priority": "core", "requires_auth": True, "premium_only": False},
        {"name": "role_management", "description": "Role-based access control", "priority": "core", "requires_auth": True, "premium_only": False}
    ],
    "entities": [
        {"name": "User", "attributes": ["id", "email", "password_hash", "name", "role", "plan"], "relations": ["Contact"]},
        {"name": "Contact", "attributes": ["id", "name", "email", "phone", "company", "status", "owner_id"], "relations": ["User"]},
        {"name": "Subscription", "attributes": ["id", "user_id", "plan", "status", "started_at", "expires_at"], "relations": ["User"]}
    ],
    "roles": [
        {"name": "admin", "permissions": ["manage_users", "view_analytics", "manage_contacts", "manage_billing"], "is_default": False},
        {"name": "manager", "permissions": ["manage_contacts", "view_dashboard"], "is_default": False},
        {"name": "user", "permissions": ["view_contacts", "edit_own_contacts", "view_dashboard"], "is_default": True}
    ],
    "actions": [
        {"name": "create_contact", "actor": "user", "target_entity": "Contact", "requires_premium": False},
        {"name": "view_analytics", "actor": "admin", "target_entity": None, "requires_premium": True},
        {"name": "manage_subscription", "actor": "user", "target_entity": "Subscription", "requires_premium": False}
    ],
    "constraints": ["Only admins can view analytics", "Premium plan required for advanced analytics", "Users can only edit their own contacts"],
    "monetization": "freemium",
    "ambiguities": [
        {"area": "analytics_access", "description": "Whether managers can also see analytics", "assumption": "Only admins can see analytics as stated"},
        {"area": "payment_provider", "description": "Which payment provider to use", "assumption": "Using Stripe as default payment provider"}
    ],
    "assumptions": ["Stripe for payments", "JWT for authentication", "Email-based login", "Three-tier role hierarchy"]
}

CRM_ARCHITECTURE = {
    "app_name": "crm_platform",
    "modules": [
        {"name": "auth", "description": "Authentication and authorization", "features": ["user_auth", "role_management"], "entities": ["User"]},
        {"name": "contacts", "description": "Contact management", "features": ["contacts_management"], "entities": ["Contact"]},
        {"name": "dashboard", "description": "Dashboard and overview", "features": ["dashboard"], "entities": []},
        {"name": "analytics", "description": "Analytics and reporting", "features": ["analytics"], "entities": []},
        {"name": "billing", "description": "Subscription and payments", "features": ["payments"], "entities": ["Subscription"]}
    ],
    "page_map": [
        {"name": "login", "route": "/login", "module": "auth", "requires_auth": False, "allowed_roles": [], "description": "Login page"},
        {"name": "register", "route": "/register", "module": "auth", "requires_auth": False, "allowed_roles": [], "description": "Registration page"},
        {"name": "dashboard", "route": "/dashboard", "module": "dashboard", "requires_auth": True, "allowed_roles": ["admin", "manager", "user"], "description": "Main dashboard"},
        {"name": "contacts", "route": "/contacts", "module": "contacts", "requires_auth": True, "allowed_roles": ["admin", "manager", "user"], "description": "Contacts list"},
        {"name": "contact_detail", "route": "/contacts/:id", "module": "contacts", "requires_auth": True, "allowed_roles": ["admin", "manager", "user"], "description": "Contact detail"},
        {"name": "analytics", "route": "/analytics", "module": "analytics", "requires_auth": True, "allowed_roles": ["admin"], "description": "Analytics dashboard"},
        {"name": "billing", "route": "/billing", "module": "billing", "requires_auth": True, "allowed_roles": ["admin", "manager", "user"], "description": "Billing and subscription"},
        {"name": "settings", "route": "/settings", "module": "auth", "requires_auth": True, "allowed_roles": ["admin"], "description": "System settings"}
    ],
    "entity_model": [
        {"name": "User", "attributes": [{"name": "id", "type": "uuid", "required": True, "unique": True}, {"name": "email", "type": "email", "required": True, "unique": True}, {"name": "password_hash", "type": "string", "required": True, "unique": False}, {"name": "name", "type": "string", "required": True, "unique": False}, {"name": "role", "type": "enum", "required": True, "unique": False}, {"name": "plan", "type": "enum", "required": True, "unique": False}], "relations": [{"target": "Contact", "type": "one_to_many", "field": "owner_id"}, {"target": "Subscription", "type": "one_to_one", "field": "user_id"}]},
        {"name": "Contact", "attributes": [{"name": "id", "type": "uuid", "required": True, "unique": True}, {"name": "name", "type": "string", "required": True, "unique": False}, {"name": "email", "type": "email", "required": False, "unique": False}, {"name": "phone", "type": "string", "required": False, "unique": False}, {"name": "company", "type": "string", "required": False, "unique": False}, {"name": "status", "type": "enum", "required": True, "unique": False}, {"name": "owner_id", "type": "uuid", "required": True, "unique": False}], "relations": [{"target": "User", "type": "many_to_one", "field": "owner_id"}]},
        {"name": "Subscription", "attributes": [{"name": "id", "type": "uuid", "required": True, "unique": True}, {"name": "user_id", "type": "uuid", "required": True, "unique": True}, {"name": "plan", "type": "enum", "required": True, "unique": False}, {"name": "status", "type": "enum", "required": True, "unique": False}, {"name": "started_at", "type": "datetime", "required": True, "unique": False}, {"name": "expires_at", "type": "datetime", "required": False, "unique": False}], "relations": [{"target": "User", "type": "one_to_one", "field": "user_id"}]}
    ],
    "role_model": [
        {"name": "admin", "level": 0, "inherits_from": ["manager"], "capabilities": ["manage_users", "view_analytics", "manage_billing", "manage_contacts"]},
        {"name": "manager", "level": 1, "inherits_from": ["user"], "capabilities": ["manage_contacts", "view_dashboard"]},
        {"name": "user", "level": 2, "inherits_from": [], "capabilities": ["view_contacts", "edit_own_contacts", "view_dashboard"]}
    ],
    "feature_map": {"auth": ["user_auth", "role_management"], "contacts": ["contacts_management"], "dashboard": ["dashboard"], "analytics": ["analytics"], "billing": ["payments"]},
    "flows": [
        {"name": "user_registration", "actor": "user", "steps": ["Navigate to register", "Fill registration form", "Submit", "Verify email", "Login"], "pages_involved": ["register", "login"]},
        {"name": "contact_creation", "actor": "user", "steps": ["Navigate to contacts", "Click create", "Fill form", "Submit", "View contact"], "pages_involved": ["contacts", "contact_detail"]}
    ],
    "tech_decisions": ["JWT authentication", "RESTful API design", "Role-based access control", "Freemium monetization model"]
}
