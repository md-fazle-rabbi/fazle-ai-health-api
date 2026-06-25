"""Health, version, and LLM connectivity endpoints.

Route structure:
  GET /health    â†’ API liveness check
  GET /version   â†’ Current API version
  GET /ping-llm  â†’ Gemini API reachability + latency
"""

import time
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.config import Settings, get_settings
from app.exceptions import LLMConnectionError, LLMResponseParseError
from app.schemas import HealthResponse, LLMPingResponse, VersionResponse

router = APIRouter(tags=["health"])

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="API Liveness Check",
)
async def health_check(
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthResponse:
    """Return API health status. Used by Render/Railway health check probes."""
    return HealthResponse(
        status="ok",
        environment=settings.app_env,
    )

@router.get(
    "/version",
    response_model=VersionResponse,
    summary="API Version Info",
)
async def get_version(
    settings: Annotated[Settings, Depends(get_settings)],
) -> VersionResponse:
    """Return API name and current version from environment config."""
    return VersionResponse(
        api_name="fazle-ai-health-api",
        version=settings.app_version,
    )

@router.get(
    "/ping-llm",
    response_model=LLMPingResponse,
    summary="Ping Gemini LLM API",
)
async def ping_llm(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> LLMPingResponse:
    """Ping Gemini API to verify connectivity and measure response latency."""
    
    url = (
        f"{settings.llm_base_url}"
        f"/models/{settings.llm_model}:generateContent"
    )

    headers = {
        "x-goog-api-key": settings.gemini_api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "contents": [
            {"parts": [{"text": "Reply with exactly one word: pong"}]}
        ]
    }

    http_client: httpx.AsyncClient = request.app.state.http_client

    start_time = time.monotonic()

    try:
        response = await http_client.post(
            url,
            headers=headers,
            json=payload,
            timeout=settings.llm_timeout_seconds,
        )
        response.raise_for_status()

        latency_ms = round((time.monotonic() - start_time) * 1000, 2)

        try:
            data = response.json()
            text: str = data["candidates"][0]["content"]["parts"][0]["text"]
            preview = text.strip()[:100]
        except (KeyError, IndexError, ValueError) as exc:
            raise LLMResponseParseError(
                f"Unexpected Gemini response shape: {exc}"
            ) from exc
        
        return LLMPingResponse(
            status="reachable",
            model=settings.llm_model,
            response_preview=preview,
            latency_ms=latency_ms,
        )
    
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Gemini API timed out after {settings.llm_timeout_seconds}s",
        ) from exc

    except httpx.ConnectError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cannot connect to Gemini API â€” check network or base URL",
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini API error: HTTP {exc.response.status_code} — {exc.response.text[:200]}",
        ) from exc

    except LLMResponseParseError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
