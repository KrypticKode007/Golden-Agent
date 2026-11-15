from enum import StrEnum
import json
import os
from typing import Any
import urllib.request
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
    """Routes requests across Tier 1/2/3 local (Ollama) and cloud (OpenAI/Anthropic/Gemini) endpoints.
    Uses LiteLLM if installed, with a zero-dependency HTTP fallback for lightweight environments like Termux.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

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

        try:
            import litellm  # type: ignore[import-untyped]

            litellm.drop_params = True
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
            choice = raw.choices[0]  # type: ignore[index]
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
        except ImportError:
            return await self._http_fallback_complete(model, messages, temperature)

    async def _http_fallback_complete(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float,
    ) -> LLMResponse:
        import asyncio

        if model.startswith("ollama/"):
            url = f"{self.settings.ollama_base_url.rstrip('/')}/v1/chat/completions"
            clean_model = model.removeprefix("ollama/")
            api_key = "ollama"
        else:
            url = os.environ.get("OPENAI_BASE_URL", "https://openai.com") + "/chat/completions"
            clean_model = model.split("/", 1)[-1]
            api_key = os.environ.get("OPENAI_API_KEY", "")

        payload = json.dumps(
            {"model": clean_model, "messages": messages, "temperature": temperature}
        ).encode("utf-8")

        def _post() -> dict[str, Any]:
            req = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}", "User-Agent": "Golden-Agent/1.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))

        data = await asyncio.to_thread(_post)
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return LLMResponse(
            content=content,
            model_used=model,
            prompt_tokens=int(usage.get("prompt_tokens", 0)),
            completion_tokens=int(usage.get("completion_tokens", 0)),
            cost_usd=0.0,
        )


    async def complete_with_retry(
        self,
        messages: list[dict[str, str]],
        tier: ModelTier = ModelTier.STANDARD,
        force_local: bool = False,
        temperature: float = 0.2,
        response_format: dict[str, Any] | None = None,
        max_retries: int = 3,
        base_delay: float = 0.2,
    ) -> LLMResponse:
        """Execute completion with exponential backoff on transient network or rate-limit errors."""
        import asyncio
        import urllib.error

        last_exc: Exception | None = None
        for attempt in range(max_retries):
            try:
                return await self.complete(
                    messages=messages,
                    tier=tier,
                    force_local=force_local,
                    temperature=temperature,
                    response_format=response_format,
                )
            except urllib.error.HTTPError as exc:
                if exc.code not in {408, 429, 500, 502, 503, 504} or attempt == max_retries - 1:
                    raise
                last_exc = exc
            except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
                if attempt == max_retries - 1:
                    raise
                last_exc = exc
            await asyncio.sleep(base_delay * (2**attempt))
        assert last_exc is not None
        raise last_exc

    @staticmethod
    def extract_json(raw_text: str) -> Any:
        """Safely extract JSON object or array from noisy LLM outputs or markdown code fences."""
        import re
        cleaned = raw_text.strip()
        fence = re.search(r"```(?:json)?\s*([\s\(\S\)]*?)```", cleaned)
        if fence:
            cleaned = fence.group(1).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        for opener, closer in [("{", "}"), ("[", "]")]:
            start = cleaned.find(opener)
            end = cleaned.rfind(closer)
            if start != -1 and end != -1 and end > start:
                return json.loads(cleaned[start : end + 1])
        raise ValueError(f"Could not extract valid JSON from model response: {raw_text[:120]}")
