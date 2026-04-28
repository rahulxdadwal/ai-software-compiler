"""API schema — Stage 3 sub-output.

Defines endpoints, methods, request/response contracts, and validation.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class FieldDefinition(BaseModel):
    """A field in a request or response contract."""
    name: str
    type: str = Field(..., description="string | integer | boolean | float | date | email | array | object")
    required: bool = Field(default=True)
    description: Optional[str] = None
    validation: Optional[str] = Field(default=None, description="Validation rule")
    enum_values: list[str] = Field(default_factory=list)


class RequestContract(BaseModel):
    """Request body or query parameter contract."""
    content_type: str = Field(default="application/json")
    fields: list[FieldDefinition] = Field(default_factory=list)


class ResponseContract(BaseModel):
    """Response body contract."""
    status_code: int = Field(default=200)
    content_type: str = Field(default="application/json")
    fields: list[FieldDefinition] = Field(default_factory=list)
    is_list: bool = Field(default=False, description="Whether response is a list of items")


class APIEndpoint(BaseModel):
    """A single API endpoint definition."""
    path: str = Field(..., description="URL path, e.g. '/api/contacts'")
    method: HttpMethod
    name: str = Field(..., description="Endpoint name, e.g. 'list_contacts'")
    description: str = Field(default="")
    module: str = Field(..., description="Owning module")
    requires_auth: bool = Field(default=False)
    allowed_roles: list[str] = Field(default_factory=list)
    request: Optional[RequestContract] = None
    response: ResponseContract = Field(default_factory=ResponseContract)
    rate_limited: bool = Field(default=False)
    premium_only: bool = Field(default=False)
    related_entity: Optional[str] = Field(default=None, description="Primary DB entity")


class APISchema(BaseModel):
    """Complete API configuration."""

    model_config = {"extra": "forbid"}

    base_url: str = Field(default="/api")
    version: str = Field(default="v1")
    endpoints: list[APIEndpoint] = Field(..., min_length=1)
    auth_type: str = Field(default="jwt", description="jwt | api_key | session")
