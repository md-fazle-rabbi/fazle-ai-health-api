"""Aggregate latency metrics endpoint with Langfuse dashboard link."""

import statistics
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.config import Settings, get_settings
from app.schemas import EndpointMetrics, MetricsResponse

router = APIRouter(tags=["observability"])

TRACKED_PATHS = {"/health", "/version", "/ping-llm", "/metrics", "/mcp-info"}


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Aggregate Endpoint Latency Metrics",
)
async def get_metrics(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> MetricsResponse:
    """Return in-memory latency metrics for all endpoints."""
    raw_store: dict = request.app.state.metrics_store

    endpoint_metrics: dict[str, EndpointMetrics] = {}
    total_requests = 0

    for path, data in raw_store.items():
        calls = data["total_calls"]
        total_requests += calls
        latencies = data["latencies_ms"]

        endpoint_metrics[path] = EndpointMetrics(
            total_calls=calls,
            avg_latency_ms=round(statistics.mean(latencies), 2) if latencies else 0.0,
            min_latency_ms=round(min(latencies), 2) if latencies else 0.0,
            max_latency_ms=round(max(latencies), 2) if latencies else 0.0,
            error_count=data["error_count"],
        )

    project_id = settings.langfuse_project_id
    dashboard_url = (
        f"https://cloud.langfuse.com/project/{project_id}/traces"
        if project_id
        else "https://cloud.langfuse.com (set LANGFUSE_PROJECT_ID in .env)"
    )

    return MetricsResponse(
        endpoints=endpoint_metrics,
        total_requests=total_requests,
        langfuse_dashboard_url=dashboard_url,
    )
