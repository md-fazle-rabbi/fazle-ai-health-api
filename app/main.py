"""FastAPI application factory with lifespan, Langfuse, and metrics middleware."""

import time
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
from fastapi import FastAPI, Request, Response

from app.config import get_settings
from app.routers import health, metrics, mcp_info
from app.tracing import langfuse

TRACKED_PATHS = {"/health", "/version", "/ping-llm", "/metrics", "/mcp-info"}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage startup and shutdown of all shared resources."""

    # ── STARTUP ──────────────────────────────────────────────
    # Shared HTTP client — TCP connection pool reuse।
    app.state.http_client = httpx.AsyncClient()

    # In-memory metrics store।
    app.state.metrics_store = defaultdict(
        lambda: {"total_calls": 0, "latencies_ms": [], "error_count": 0}
    )

    yield

    # ── SHUTDOWN ─────────────────────────────────────────────
    await app.state.http_client.aclose()

    langfuse.flush()


def create_app() -> FastAPI:
    """Application factory — returns configured FastAPI instance."""
    settings = get_settings()

    app = FastAPI(
        title="fazle-ai-health-api",
        description=(
            "Production-grade AI Health API with Langfuse observability. "
            "Built with FastAPI, Pydantic V2, Gemini free tier, and MCP-ready architecture."
        ),
        version=settings.app_version,
        lifespan=lifespan,
    )

    # ── Metrics Middleware ────────────────────────────────────
    @app.middleware("http")
    async def latency_tracking_middleware(
        request: Request, call_next
    ) -> Response:
        start = time.monotonic()
        response: Response = await call_next(request)
        latency_ms = round((time.monotonic() - start) * 1000, 2)

        path = request.url.path
        if path in TRACKED_PATHS:
            store = request.app.state.metrics_store[path]
            store["total_calls"] += 1
            store["latencies_ms"].append(latency_ms)
            # 4xx/5xx = error।
            if response.status_code >= 400:
                store["error_count"] += 1

        return response

    # ── Routers ───────────────────────────────────────────────
    app.include_router(health.router)
    app.include_router(metrics.router)
    app.include_router(mcp_info.router)

    return app


app = create_app()
