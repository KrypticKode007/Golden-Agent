from enum import StrEnum
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExecutionMode(StrEnum):
    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="GOLDEN_",
        extra="ignore",
    )

    app_name: str = "Golden-Agent"
    environment: str = "development"
    execution_mode: ExecutionMode = ExecutionMode.HYBRID

    # Local Ollama / vLLM Endpoint
    ollama_base_url: str = "http://localhost:11434"

    # Model Tiers
    tier1_cloud_model: str = "gemini/gemini-2.5-flash"
    tier2_cloud_model: str = "anthropic/claude-sonnet-4-20250514"
    tier3_cloud_model: str = "anthropic/claude-opus-4-20250514"

    tier1_local_model: str = "ollama/qwen2.5:7b"
    tier2_local_model: str = "ollama/qwen2.5-coder:32b"
    tier3_local_model: str = "ollama/deepseek-r1:32b"

    # Context & Budget Controls
    max_context_tokens: int = 128_000
    compression_threshold: float = Field(default=0.70, ge=0.3, le=0.95)
    max_verifier_retries: int = 3
    max_parallel_workers: int = 5

    # Sandbox & Storage
    docker_sandbox_image: str = "python:3.11-slim"
    sandbox_timeout_seconds: int = 30
    sandbox_memory_limit: str = "512m"
    qdrant_url: str = "http://localhost:6333"
    workspace_root: str = "."


@lru_cache
def get_settings() -> Settings:
    return Settings()
  
