"""UI schema — Stage 3 sub-output.

Defines pages, layouts, components, forms, tables, and navigation.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ComponentType(str, Enum):
    FORM = "form"
    TABLE = "table"
    CARD = "card"
    CHART = "chart"
    LIST = "list"
    MODAL = "modal"
    BUTTON = "button"
    STAT = "stat"
    TABS = "tabs"
    SIDEBAR = "sidebar"
    HEADER = "header"


class LayoutType(str, Enum):
    SINGLE_COLUMN = "single_column"
    TWO_COLUMN = "two_column"
    DASHBOARD_GRID = "dashboard_grid"
    SIDEBAR_MAIN = "sidebar_main"
    FULL_WIDTH = "full_width"


class FormField(BaseModel):
    """A field inside a form component."""
    name: str
    label: str
    field_type: str = Field(..., description="text | email | password | number | select | textarea | checkbox | date")
    required: bool = Field(default=False)
    validation: Optional[str] = Field(default=None, description="Validation rule description")
    options: list[str] = Field(default_factory=list, description="Options for select fields")


class TableColumn(BaseModel):
    """A column inside a table component."""
    key: str
    label: str
    sortable: bool = Field(default=False)
    filterable: bool = Field(default=False)


class UIComponent(BaseModel):
    """A UI component on a page."""
    id: str = Field(..., description="Unique component identifier")
    type: ComponentType
    title: Optional[str] = None
    fields: list[FormField] = Field(default_factory=list, description="For form components")
    columns: list[TableColumn] = Field(default_factory=list, description="For table components")
    data_source: Optional[str] = Field(default=None, description="API endpoint that feeds this component")
    actions: list[str] = Field(default_factory=list, description="Action buttons")
    premium_only: bool = Field(default=False)


class UIPage(BaseModel):
    """A page definition in the UI."""
    name: str
    route: str
    title: str
    layout: LayoutType = Field(default=LayoutType.SINGLE_COLUMN)
    components: list[UIComponent] = Field(default_factory=list)
    requires_auth: bool = Field(default=False)
    allowed_roles: list[str] = Field(default_factory=list)


class NavItem(BaseModel):
    """A navigation menu item."""
    label: str
    route: str
    icon: Optional[str] = None
    visible_to: list[str] = Field(default_factory=list, description="Roles that can see this")
    premium_only: bool = Field(default=False)


class UISchema(BaseModel):
    """Complete UI configuration."""

    model_config = {"extra": "forbid"}

    pages: list[UIPage] = Field(..., min_length=1)
    navigation: list[NavItem] = Field(..., min_length=1)
    theme: dict = Field(default_factory=lambda: {
        "primary_color": "#6366f1",
        "mode": "light"
    })
