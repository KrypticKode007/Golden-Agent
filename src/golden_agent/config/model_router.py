from enum import StrEnum
from typing import Any
import litellm
from pydantic import BaseModel
from golden_agent.config.settings import ExecutionMode, Settings, get_settings


class ModelTier(StrEnum):
    FAST = "tier1_fast"
    STANDARD = "tier2_standard"
    FRONTIER = "tier3_frontier"


class LLMResponse(BaseModel):
    content: str
    model_used: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0


class ModelRouter:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        litellm.drop_params = True

    def resolve_model(self, tier: ModelTier, force_local: bool = False) -> str:
        use_local = force_local or self.settings.execution_mode == ExecutionMode.LOCAL

        if use_local:
            return {
                ModelTier.FAST: self.settings.tier1_local_model,
                ModelTier.STANDARD: self.settings.tier2_local_model,
                ModelTier.FRONTIER: self.settings.tier3_local_model,
            }[tier]

        if self.settings.execution_mode == ExecutionMode.HYBRID and tier == ModelTier.FAST:
            return self.settings.tier1_local_model

        return {
            ModelTier.FAST: self.settings.tier1_cloud_model,
            ModelTier.STANDARD: self.settings.tier2_cloud_model,
            ModelTier.FRONTIER: self.settings.tier3_cloud_model,
        }[tier]

    async def complete(
        self,
        messages: list[dict[str, str]],
        tier: ModelTier = ModelTier.STANDARD,
        force_local: bool = False,
        temperature: float = 0.2,
        response_format: dict[str, Any] | None = None,
    ) -> LLMResponse:
        model = self.resolve_model(tier=tier, force_local=force_local)
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if model.startswith("ollama/"):
            kwargs["api_base"] = self.settings.ollama_base_url
        if response_format is not None:
            kwargs["response_format"] = response_format

        raw = await litellm.acompletion(**kwargs)
        choice = raw.choices[0]  # type: ignore[union-attr]
        usage = getattr(raw, "usage", None)

        prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
        completion_tokens = getattr(usage, "completion_tokens", 0) or 0

        try:
            cost = float(litellm.completion_cost(completion_response=raw))
        except Exception:
            cost = 0.0

        return LLMResponse(
            content=choice.message.content or "",
            model_used=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost,
              )
      
