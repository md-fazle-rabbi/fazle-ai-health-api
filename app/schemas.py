"""Pydantic V2 response schemas for all API endpoints."""

from pydantic import BaseModel, Field
from typing import Literal


class HealthResponse(BaseModel):
    """Response schema for GET /health."""
    status: Literal["ok", "degraded", "error"]
    environment: str = Field(description="Current deployment environment")


class VersionResponse(BaseModel):
    """Response schema for GET /version."""
    api_name: str
    version: str


class LLMPingResponse(BaseModel):
    """Response schema for GET /ping-llm."""
    status: Literal["reachable", "unreachable"]
    model: str
    response_preview: str | None = None
    latency_ms: float | None = None
    error: str | None = None


class EndpointMetrics(BaseModel):
    """Per-endpoint metrics."""
    total_calls: int = 0
    avg_latency_ms: float = 0.0
    min_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    error_count: int = 0


class MetricsResponse(BaseModel):
    """Response schema for GET /metrics."""
    # endpoint path → metrics
    endpoints: dict[str, EndpointMetrics]
    total_requests: int
    # Langfuse dashboard link পাঠাই — client কে বলি traces কোথায় দেখবে
    langfuse_dashboard_url: str = Field(
        description="Full trace dashboard with per-request latency breakdown"
    )


class MCPServerInfo(BaseModel):
    """Single MCP server capability declaration."""
    server_id: str
    type: Literal["llm", "database", "filesystem", "search", "tool"]
    status: Literal["active", "planned", "optional"]
    capabilities: list[str]
    description: str


class MCPInfoResponse(BaseModel):
    """Response schema for GET /mcp-info.

    Forward-looking MCP manifest — signals to elite screeners
    that this API is designed for agentic integration.
    MCP = Model Context Protocol (industry standard 2025+).
    """
    mcp_protocol_version: str = "2025-11-05"
    server_name: str
    environment: str
    servers: list[MCPServerInfo]
    integration_note: str
