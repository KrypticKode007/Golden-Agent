from pathlib import Path
from typing import Any
from pydantic import BaseModel


class DomainProfile(BaseModel):
    name: str = "universal"
    description: str = ""
    default_worker: str = "coder"
    require_approval_for_writes: bool = False
    verify_with_sandbox: bool = True
    system_prompt: str = "You are Golden-Agent."


def _parse_simple_yaml(raw: str) -> dict[str, Any]:
    try:
        import yaml  # type: ignore[import-untyped]

        return yaml.safe_load(raw) or {}
    except ImportError:
        out: dict[str, Any] = {}
        for line in raw.splitlines():
            if ":" not in line or line.startswith((" ", "#")):
                continue
            k, v = line.split(":", 1)
            val = v.strip()
            if val.lower() in ("true", "false"):
                out[k.strip()] = val.lower() == "true"
            elif val != ">":
                out[k.strip()] = val
        return out


def load_profile(name: str, profiles_dir: str | Path = "profiles") -> DomainProfile:
    path = Path(profiles_dir) / f"{name}.yaml"
    if not path.is_file():
        return DomainProfile(name=name)
    data = _parse_simple_yaml(path.read_text(encoding="utf-8"))
    loader = getattr(DomainProfile, "model_validate", None) or DomainProfile.parse_obj
    return loader(data)
