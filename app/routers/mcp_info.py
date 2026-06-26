"""MCP capability manifest endpoint.

MCP = Model Context Protocol (Anthropic, 2024, industry standard by 2025)."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.schemas import MCPInfoResponse, MCPServerInfo

router = APIRouter(tags=["observability"])


@router.get(
    "/mcp-info",
    response_model=MCPInfoResponse,
    summary="MCP Integration Manifest",
)
async def get_mcp_info(
    settings: Annotated[Settings, Depends(get_settings)],
) -> MCPInfoResponse:
    """Return MCP capability manifest for agentic integration.

    Forward-looking signal: shows architectural awareness of
    Model Context Protocol for LLM tool-use patterns.
    """
    return MCPInfoResponse(
        server_name="fazle-ai-health-api",
        environment=settings.app_env,
        servers=[
            MCPServerInfo(
                server_id="gemini-llm",
                type="llm",
                status="active",
                capabilities=[
                    "generateContent",
                    "countTokens",
                    "streamGenerateContent",
                ],
                description="Gemini free-tier LLM — currently wired to /ping-llm",
            ),
            MCPServerInfo(
                server_id="postgresql-rag",
                type="database",
                status="planned",
                capabilities=[
                    "semantic_search",
                    "row_level_security",
                    "vector_similarity",
                ],
                description="pgvector RAG backend — fazle-secure-rag-pipeline",
            ),
            MCPServerInfo(
                server_id="langfuse-observability",
                type="tool",
                status="active",
                capabilities=[
                    "trace_llm_calls",
                    "latency_monitoring",
                    "cost_tracking",
                    "prompt_management",
                ],
                description="LLM observability — all routes instrumented",
            ),
            MCPServerInfo(
                server_id="web-search",
                type="search",
                status="optional",
                capabilities=["search", "fetch_url", "extract_content"],
                description="Planned: Tavily/Brave search for RAG grounding",
            ),
        ],
        integration_note=(
            "This API is designed as an MCP-compatible backend. "
            "Each server_id maps to a deployable MCP server configuration. "
            "Active servers are live; planned servers are next sprint."
        ),
    )
