# fazle-ai-health-api

> Production-grade AI Health API with Gemini integration and Langfuse observability.
> Built to demonstrate elite async Python API delivery — deployed, instrumented, and OWASP-aware.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=flat&logo=python)](https://python.org)
[![Pydantic](https://img.shields.io/badge/Pydantic-V2-E92063?style=flat)](https://docs.pydantic.dev)
[![Langfuse](https://img.shields.io/badge/Langfuse-Traced-FF6B35?style=flat)](https://langfuse.com)
[![Docker](https://img.shields.io/badge/Docker-Multi--stage-2496ED?style=flat&logo=docker)](https://docker.com)
[![uv](https://img.shields.io/badge/uv-Package%20Manager-DE5FE9?style=flat)](https://docs.astral.sh/uv)

---

## Live Demo

| Endpoint | URL |
|---|---|
| Swagger UI | `https://fazle-ai-health-api.onrender.com/docs` |
| Health Check | `https://fazle-ai-health-api.onrender.com/health` |
| LLM Ping | `https://fazle-ai-health-api.onrender.com/ping-llm` |
| Metrics | `https://fazle-ai-health-api.onrender.com/metrics` |
| MCP Info | `https://fazle-ai-health-api.onrender.com/mcp-info` |

> **Note:** Hosted on Render free tier — first request may take 30s (cold start).

---

## What Makes This Production-Grade

| Pattern | Implementation |
|---|---|
| Modern lifespan (not deprecated `@app.on_event`) | `@asynccontextmanager` in `main.py` |
| Pydantic V2 strict schemas | All request/response models validated |
| LLM observability | Langfuse traces on every endpoint |
| Shared async HTTP client | `httpx.AsyncClient` via `app.state` |
| Non-root Docker container | `appuser` in multi-stage Dockerfile |
| Secrets via environment | `pydantic-settings` — zero hardcoded keys |
| OWASP LLM06 compliant | `.env` gitignored, `sync: false` on Render |
| uv package management | 100x faster than pip, locked dependencies |

---

## Endpoints

### `GET /health`
API liveness check. Used by Render health probe.
```json
{"status": "ok", "environment": "production"}
```

### `GET /version`
Returns API name and semantic version.
```json
{"api_name": "fazle-ai-health-api", "version": "1.0.0"}
```

### `GET /ping-llm`
Pings Gemini 2.5 Flash API and returns latency.
```json
{
  "status": "reachable",
  "model": "gemini-2.5-flash",
  "response_preview": "pong",
  "latency_ms": 1533.28,
  "error": null
}
```

### `GET /metrics`
In-memory latency metrics per endpoint + Langfuse dashboard link.
```json
{
  "endpoints": {
    "/health": {"total_calls": 5, "avg_latency_ms": 12.3},
    "/ping-llm": {"total_calls": 2, "avg_latency_ms": 1533.28}
  },
  "total_requests": 7,
  "langfuse_dashboard_url": "https://cloud.langfuse.com/project/..."
}
```

### `GET /mcp-info`
Declarative MCP capability manifest for agentic integration.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.116+ |
| Validation | Pydantic V2 |
| LLM Provider | Gemini 2.5 Flash (free tier) |
| Observability | Langfuse v4 |
| HTTP Client | httpx (async) |
| Package Manager | uv |
| Containerisation | Docker (multi-stage) |
| Deploy | Render (free tier) |
| Python | 3.14 |

---

## Project Structure

fazle-ai-health-api/

├── app/

│   ├── main.py           # FastAPI factory + lifespan + middleware

│   ├── config.py         # pydantic-settings (reads .env)

│   ├── schemas.py        # Pydantic V2 response models

│   ├── tracing.py        # Langfuse singleton

│   ├── exceptions.py     # Custom exception classes

│   └── routers/

│       ├── health.py     # /health /version /ping-llm

│       ├── metrics.py    # /metrics

│       └── mcp_info.py   # /mcp-info

├── Dockerfile            # Multi-stage uv build

├── render.yaml           # Render IaC config

├── pyproject.toml        # uv dependencies

└── .env.example          # Environment variable template

---

## Local Setup

### Prerequisites
- Python 3.14
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Gemini API key → [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
- Langfuse account (free) → [cloud.langfuse.com](https://cloud.langfuse.com)

### Run locally

```bash
# Clone
git clone https://github.com/md-fazle-rabbi/fazle-ai-health-api
cd fazle-ai-health-api

# Copy env template
cp .env.example .env
# Fill in GEMINI_API_KEY + LANGFUSE keys in .env

# Install dependencies
uv sync

# Run
uv run uvicorn app.main:app --reload
```

Open: `http://localhost:8000/docs`

### Run with Docker

```bash
docker build -t fazle-ai-health-api .
docker run --rm -p 8001:8000 --env-file .env fazle-ai-health-api
```

Open: `http://localhost:8001/docs`

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | ✅ | Google AI Studio API key |
| `LANGFUSE_SECRET_KEY` | ✅ | Langfuse secret key |
| `LANGFUSE_PUBLIC_KEY` | ✅ | Langfuse public key |
| `LANGFUSE_PROJECT_ID` | ✅ | Langfuse project ID |
| `APP_ENV` | ❌ | `development` / `production` (default: development) |
| `APP_VERSION` | ❌ | Semantic version (default: 1.0.0) |
| `LLM_MODEL` | ❌ | Gemini model ID (default: gemini-2.5-flash) |
| `LLM_TIMEOUT_SECONDS` | ❌ | LLM request timeout (default: 10) |

See `.env.example` for full template.

---

## Security

- **OWASP LLM06** — No secrets in code or Docker image. All keys via environment variables.
- **Non-root container** — Runs as `appuser`, not root.
- **Input validation** — Pydantic V2 strict mode on all schemas.
- **Graceful degradation** — Langfuse disabled if keys missing (no crash).

---

## Freelance Services

This project is part of my production AI engineering portfolio.

**Available for:**
- FastAPI + LLM integration ($350 fixed)
- RAG pipeline with pgvector ($799 fixed)
- LangGraph agent + MCP integration ($599 fixed)
- OWASP LLM security audit ($450 fixed)

---

## Author

**Fazle Rabbi**
AI Engineer · FastAPI · LangGraph · MCP · OWASP LLM:2025 + Agentic:2026

