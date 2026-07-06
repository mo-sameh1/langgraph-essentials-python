"""Environment-backed settings for local model access."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Course settings loaded from environment variables or a local `.env` file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "langgraph-coder"
    ollama_num_ctx: int = Field(default=32768, ge=4096)
    ollama_temperature: float = Field(default=0.2, ge=0.0, le=2.0)


@lru_cache
def get_settings() -> Settings:
    """Return one validated settings instance per process."""

    return Settings()
