from enum import StrEnum
from functools import lru_cache
import os
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field


class ExecutionMode(StrEnum):
    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


def _load_dotenv(path: str = ".env") -> None:
    env_file = Path(path)
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


class Settings(BaseModel):
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

    def __init__(self, **data: Any) -> None:
        _load_dotenv()
        field_names = getattr(type(self), "model_fields", None) or getattr(
            type(self), "__fields__", {}
        )
        env_overrides: dict[str, Any] = {}
        for field_name in field_names:
            env_key = f"GOLDEN_{field_name.upper()}"
            if env_key in os.environ and field_name not in data:
                env_overrides[field_name] = os.environ[env_key]
        super().__init__(**{**env_overrides, **data})


@lru_cache
def get_settings() -> Settings:
    return Settings()
