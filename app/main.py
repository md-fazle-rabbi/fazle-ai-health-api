"""FastAPI application factory with lifespan context manager."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
from fastapi import FastAPI

from app.config import get_settings
from app.routers import health

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage startup and shutdown of shared resources."""

    app.state.http_client = httpx.AsyncClient()

    yield

    await app.state.http_client.aclose()

def create_app() -> FastAPI:
    """Application factory — returns a fully configured FastAPI instance."""
    settings = get_settings()

    app = FastAPI(
        title="fazle-ai-health-api",
        description=(
            "Production-grade AI Health API — freelance portfolio proof. "
            "Built with FastAPI, Pydantic V2, and Gemini free tier."
        ),
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.include_router(health.router)

    return app

app = create_app()
