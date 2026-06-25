"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Reads ALL config from .env file with full type validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    app_version: str = "1.0.0"

    gemini_api_key: str
    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    llm_model: str = "gemini-3.5-flash"
    llm_timeout_seconds: int = 10

@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""

    return Settings()