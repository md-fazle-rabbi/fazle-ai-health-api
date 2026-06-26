"""Health, version, and LLM connectivity endpoints with Langfuse tracing."""

import time
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from langfuse import propagate_attributes  # Added for v4 metadata propagation

from app.config import Settings, get_settings
from app.exceptions import LLMConnectionError, LLMResponseParseError
from app.schemas import HealthResponse, LLMPingResponse, VersionResponse
from app.tracing import langfuse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="API Liveness Check")
async def health_check(
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthResponse:
    """Return API health status."""
    # In v4, start a root observation span which implicitly initializes the trace context
    with langfuse.start_as_current_observation(
        name="health-check",
        as_type="span",
    ) as span:
        result = HealthResponse(status="ok", environment=settings.app_env)
        
        # Update the span directly with outputs and metadata
        span.update(
            output={"status": result.status},
            metadata={"endpoint": "/health", "environment": settings.app_env}
        )
        return result


@router.get("/version", response_model=VersionResponse, summary="API Version Info")
async def get_version(
    settings: Annotated[Settings, Depends(get_settings)],
) -> VersionResponse:
    """Return API name and version."""
    with langfuse.start_as_current_observation(
        name="version-check",
        as_type="span",
    ) as span:
        result = VersionResponse(api_name="fazle-ai-health-api", version=settings.app_version)
        
        span.update(
            output={"version": result.version},
            metadata={"endpoint": "/version"}
        )
        return result


@router.get("/ping-llm", response_model=LLMPingResponse, summary="Ping Gemini LLM API")
async def ping_llm(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> LLMPingResponse:
    """Ping Gemini API to verify connectivity and measure latency."""

    url = f"{settings.llm_base_url}/models/{settings.llm_model}:generateContent"
    headers = {
        "x-goog-api-key": settings.gemini_api_key,
        "Content-Type": "application/json",
    }
    payload = {"contents": [{"parts": [{"text": "Reply with exactly one word: pong"}]}]}

    # Outer root span defines the request lifetime
    with langfuse.start_as_current_observation(
        name="ping-llm",
        as_type="span",
    ) as span:
        # Use propagate_attributes to ensure context down to nested operations (like the generation)
        with propagate_attributes(metadata={"endpoint": "/ping-llm", "model": settings.llm_model}):
            # Nested generation span for the specific LLM call
            with langfuse.start_as_current_observation(
                name="gemini-generateContent",
                as_type="generation",
                model=settings.llm_model,
                input=[{"role": "user", "content": "Reply with exactly one word: pong"}],
            ) as generation:

                http_client: httpx.AsyncClient = request.app.state.http_client
                start_time = time.monotonic()

                try:
                    response = await http_client.post(
                        url, headers=headers, json=payload,
                        timeout=settings.llm_timeout_seconds,
                    )
                    response.raise_for_status()
                    latency_ms = round((time.monotonic() - start_time) * 1000, 2)

                    try:
                        data = response.json()
                        text: str = data["candidates"][0]["content"]["parts"][0]["text"]
                        preview = text.strip()[:100]
                    except (KeyError, IndexError, ValueError) as exc:
                        raise LLMResponseParseError(f"Unexpected response shape: {exc}") from exc

                    # Update attributes directly on the context objects
                    generation.update(
                        output=preview,
                        usage={"total_tokens": len(preview.split())},
                        metadata={"latency_ms": latency_ms},
                    )
                    span.update(output={"status": "reachable", "latency_ms": latency_ms})

                    return LLMPingResponse(
                        status="reachable",
                        model=settings.llm_model,
                        response_preview=preview,
                        latency_ms=latency_ms,
                    )

                except httpx.TimeoutException as exc:
                    generation.update(level="ERROR", status_message="Timeout")
                    span.update(output={"status": "unreachable", "error": "timeout"})
                    raise HTTPException(
                        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                        detail=f"Gemini API timed out after {settings.llm_timeout_seconds}s",
                    ) from exc

                except httpx.ConnectError as exc:
                    generation.update(level="ERROR", status_message="Connection error")
                    span.update(output={"status": "unreachable", "error": "connect_error"})
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Cannot connect to Gemini API",
                    ) from exc

                except httpx.HTTPStatusError as exc:
                    generation.update(level="ERROR", status_message=f"HTTP {exc.response.status_code}")
                    span.update(output={"status": "unreachable", "error": str(exc.response.status_code)})
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Gemini API error: HTTP {exc.response.status_code} — {exc.response.text[:200]}",
                    ) from exc

                except LLMResponseParseError as exc:
                    generation.update(level="ERROR", status_message=str(exc))
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=str(exc),
                    ) from exc