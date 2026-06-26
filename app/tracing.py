"""Langfuse singleton — shared observability client."""

from langfuse import Langfuse
from app.config import get_settings

settings = get_settings()

# Module-level singleton।
langfuse = Langfuse(
    secret_key=settings.langfuse_secret_key or None,
    public_key=settings.langfuse_public_key or None,
    host=settings.langfuse_base_url,
)
