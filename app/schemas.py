"""Pydantic V2 response schemas for all API endpoints."""

from pydantic import BaseModel, Field

from typing import Literal

class HealthResponse(BaseModel):
    """Response schema for GET /health."""

    status: Literal["ok", "degraded", "error"]
    environment: str = Field(description="Current deployment environment")

class VersionResponse(BaseModel):
    """Response schema for GET /version."""

    api_name: str = Field(description="Name of this API service")
    version: str = Field(description="Current semantic version")

class LLMPingResponse(BaseModel):
    """Response schema for GET /ping-llm."""

    status: Literal["reachable", "unreachable"]
    model: str = Field(description="LLM model used for the ping")

    response_preview: str | None = Field(
        default=None,
        description="First 100 characters of LLM response",
    )
    latency_ms: float | None = Field(
        default=None,
        description="Round-trip latency in milliseconds",
    )
    error: str | None = Field(
        default=None,
        description="Error detail if LLM is unreachable",
    )