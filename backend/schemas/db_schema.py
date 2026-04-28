"""Database schema — Stage 3 sub-output.

Defines tables, columns, relations, enums, and indexes.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ColumnType(str, Enum):
    STRING = "string"
    TEXT = "text"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    EMAIL = "email"
    ENUM = "enum"
    JSON = "json"
    UUID = "uuid"


class RelationType(str, Enum):
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"


class DBColumn(BaseModel):
    """A column in a database table."""
    name: str
    type: ColumnType
    primary_key: bool = Field(default=False)
    nullable: bool = Field(default=True)
    unique: bool = Field(default=False)
    default: Optional[str] = None
    enum_values: list[str] = Field(default_factory=list, description="For enum columns")
    description: Optional[str] = None


class DBRelation(BaseModel):
    """A foreign key relation between tables."""
    target_table: str
    type: RelationType
    foreign_key: str = Field(..., description="Column name holding the FK")
    target_column: str = Field(default="id")
    on_delete: str = Field(default="CASCADE", description="CASCADE | SET_NULL | RESTRICT")


class DBIndex(BaseModel):
    """A database index."""
    name: str
    columns: list[str] = Field(..., min_length=1)
    unique: bool = Field(default=False)


class DBEnum(BaseModel):
    """A database enum type."""
    name: str
    values: list[str] = Field(..., min_length=1)


class DBTable(BaseModel):
    """A database table definition."""
    name: str
    description: Optional[str] = None
    columns: list[DBColumn] = Field(..., min_length=1)
    relations: list[DBRelation] = Field(default_factory=list)
    indexes: list[DBIndex] = Field(default_factory=list)
    timestamps: bool = Field(default=True, description="Auto-add created_at/updated_at")


class DBSchema(BaseModel):
    """Complete database schema."""

    model_config = {"extra": "forbid"}

    tables: list[DBTable] = Field(..., min_length=1)
    enums: list[DBEnum] = Field(default_factory=list)
