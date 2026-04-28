"""Mock DB, Auth, and Business Rules responses — Part 3."""

CRM_DB = {
    "tables": [
        {"name": "users", "description": "Application users", "columns": [
            {"name": "id", "type": "uuid", "primary_key": True, "nullable": False, "unique": True, "default": "gen_random_uuid()", "enum_values": [], "description": "Primary key"},
            {"name": "email", "type": "email", "primary_key": False, "nullable": False, "unique": True, "default": None, "enum_values": [], "description": "User email"},
            {"name": "password_hash", "type": "string", "primary_key": False, "nullable": False, "unique": False, "default": None, "enum_values": [], "description": "Hashed password"},
            {"name": "name", "type": "string", "primary_key": False, "nullable": False, "unique": False, "default": None, "enum_values": [], "description": "Full name"},
            {"name": "role", "type": "enum", "primary_key": False, "nullable": False, "unique": False, "default": "user", "enum_values": ["admin", "manager", "user"], "description": "User role"},
            {"name": "plan", "type": "enum", "primary_key": False, "nullable": False, "unique": False, "default": "free", "enum_values": ["free", "premium"], "description": "Subscription plan"}
        ], "relations": [], "indexes": [{"name": "idx_users_email", "columns": ["email"], "unique": True}], "timestamps": True},
        {"name": "contacts", "description": "CRM contacts", "columns": [
            {"name": "id", "type": "uuid", "primary_key": True, "nullable": False, "unique": True, "default": "gen_random_uuid()", "enum_values": [], "description": "Primary key"},
            {"name": "name", "type": "string", "primary_key": False, "nullable": False, "unique": False, "default": None, "enum_values": [], "description": "Contact name"},
            {"name": "email", "type": "email", "primary_key": False, "nullable": True, "unique": False, "default": None, "enum_values": [], "description": "Contact email"},
            {"name": "phone", "type": "string", "primary_key": False, "nullable": True, "unique": False, "default": None, "enum_values": [], "description": "Phone number"},
            {"name": "company", "type": "string", "primary_key": False, "nullable": True, "unique": False, "default": None, "enum_values": [], "description": "Company name"},
            {"name": "status", "type": "enum", "primary_key": False, "nullable": False, "unique": False, "default": "lead", "enum_values": ["lead", "active", "inactive"], "description": "Contact status"},
            {"name": "owner_id", "type": "uuid", "primary_key": False, "nullable": False, "unique": False, "default": None, "enum_values": [], "description": "FK to users"}
        ], "relations": [{"target_table": "users", "type": "many_to_one", "foreign_key": "owner_id", "target_column": "id", "on_delete": "CASCADE"}], "indexes": [{"name": "idx_contacts_owner", "columns": ["owner_id"], "unique": False}, {"name": "idx_contacts_status", "columns": ["status"], "unique": False}], "timestamps": True},
        {"name": "subscriptions", "description": "User subscriptions", "columns": [
            {"name": "id", "type": "uuid", "primary_key": True, "nullable": False, "unique": True, "default": "gen_random_uuid()", "enum_values": [], "description": "Primary key"},
            {"name": "user_id", "type": "uuid", "primary_key": False, "nullable": False, "unique": True, "default": None, "enum_values": [], "description": "FK to users"},
            {"name": "plan", "type": "enum", "primary_key": False, "nullable": False, "unique": False, "default": "free", "enum_values": ["free", "premium"], "description": "Plan type"},
            {"name": "status", "type": "enum", "primary_key": False, "nullable": False, "unique": False, "default": "active", "enum_values": ["active", "cancelled", "expired"], "description": "Subscription status"},
            {"name": "started_at", "type": "datetime", "primary_key": False, "nullable": False, "unique": False, "default": "now()", "enum_values": [], "description": "Start date"},
            {"name": "expires_at", "type": "datetime", "primary_key": False, "nullable": True, "unique": False, "default": None, "enum_values": [], "description": "Expiry date"}
        ], "relations": [{"target_table": "users", "type": "one_to_one", "foreign_key": "user_id", "target_column": "id", "on_delete": "CASCADE"}], "indexes": [], "timestamps": True}
    ],
    "enums": [
        {"name": "user_role", "values": ["admin", "manager", "user"]},
        {"name": "user_plan", "values": ["free", "premium"]},
        {"name": "contact_status", "values": ["lead", "active", "inactive"]},
        {"name": "subscription_status", "values": ["active", "cancelled", "expired"]}
    ]
}

CRM_AUTH = {
    "auth_type": "jwt",
    "roles": [
        {"name": "admin", "display_name": "Administrator", "level": 0, "permissions": ["users:manage", "contacts:manage", "analytics:read", "billing:manage", "settings:manage"], "is_default": False, "description": "Full system access"},
        {"name": "manager", "display_name": "Manager", "level": 1, "permissions": ["contacts:manage", "contacts:read", "dashboard:read"], "is_default": False, "description": "Can manage contacts"},
        {"name": "user", "display_name": "Standard User", "level": 2, "permissions": ["contacts:read", "contacts:write_own", "dashboard:read", "billing:read_own"], "is_default": True, "description": "Basic access"}
    ],
    "permissions": [
        {"name": "users:manage", "description": "Manage all users", "resource": "users", "action": "manage"},
        {"name": "contacts:manage", "description": "Full contact access", "resource": "contacts", "action": "manage"},
        {"name": "contacts:read", "description": "Read contacts", "resource": "contacts", "action": "read"},
        {"name": "contacts:write_own", "description": "Edit own contacts", "resource": "contacts", "action": "write"},
        {"name": "analytics:read", "description": "View analytics", "resource": "analytics", "action": "read"},
        {"name": "billing:manage", "description": "Manage billing", "resource": "billing", "action": "manage"},
        {"name": "billing:read_own", "description": "View own billing", "resource": "billing", "action": "read"},
        {"name": "dashboard:read", "description": "View dashboard", "resource": "dashboard", "action": "read"},
        {"name": "settings:manage", "description": "Manage settings", "resource": "settings", "action": "manage"}
    ],
    "route_access": [
        {"route": "/dashboard", "allowed_roles": ["admin", "manager", "user"], "requires_auth": True, "premium_only": False},
        {"route": "/contacts", "allowed_roles": ["admin", "manager", "user"], "requires_auth": True, "premium_only": False},
        {"route": "/contacts/:id", "allowed_roles": ["admin", "manager", "user"], "requires_auth": True, "premium_only": False},
        {"route": "/analytics", "allowed_roles": ["admin"], "requires_auth": True, "premium_only": True},
        {"route": "/billing", "allowed_roles": ["admin", "manager", "user"], "requires_auth": True, "premium_only": False},
        {"route": "/settings", "allowed_roles": ["admin"], "requires_auth": True, "premium_only": False}
    ],
    "token_expiry_minutes": 60,
    "refresh_enabled": True
}

CRM_BUSINESS_RULES = {
    "premium_gates": [
        {"feature": "analytics", "gate_type": "hard", "required_plan": "premium", "fallback_behavior": "show_upgrade_prompt"},
        {"feature": "advanced_export", "gate_type": "soft", "required_plan": "premium", "fallback_behavior": "show_upgrade_prompt"}
    ],
    "role_rules": [
        {"name": "admin_analytics_access", "description": "Only admins can view analytics", "role": "admin", "condition": "user.role == 'admin'", "action": "allow_analytics_access", "priority": 0},
        {"name": "user_own_contacts_only", "description": "Users can only edit their own contacts", "role": "user", "condition": "contact.owner_id == user.id", "action": "allow_edit", "priority": 1},
        {"name": "manager_all_contacts", "description": "Managers can manage all contacts", "role": "manager", "condition": "user.role in ['manager', 'admin']", "action": "allow_contact_management", "priority": 0}
    ],
    "workflows": [
        {"name": "contact_lifecycle", "description": "Contact status progression", "trigger": "contact_created", "steps": [
            {"order": 1, "name": "create_lead", "description": "Contact created as lead", "actor": "user", "action": "set_status_lead", "next_step": "qualify_lead", "condition": None},
            {"order": 2, "name": "qualify_lead", "description": "Qualify the lead", "actor": "manager", "action": "review_and_qualify", "next_step": "activate", "condition": "lead is qualified"},
            {"order": 3, "name": "activate", "description": "Activate contact", "actor": "manager", "action": "set_status_active", "next_step": None, "condition": None}
        ]}
    ],
    "constraints": [
        {"name": "unique_contact_email_per_owner", "description": "Same owner cannot have duplicate contact emails", "type": "validation", "scope": "contacts", "rule": "UNIQUE(owner_id, email) WHERE email IS NOT NULL"},
        {"name": "premium_analytics_gate", "description": "Analytics requires premium plan", "type": "dependency", "scope": "analytics", "rule": "user.plan == 'premium' AND user.role == 'admin'"}
    ]
}
