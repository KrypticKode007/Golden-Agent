"""Golden-Agent (Project Kai-007) Core Package."""

__version__ = "1.0.0"
__author__ = "KrypticKode007"
__all__ = []

def _export_module(mod):
    for _name in dir(mod):
        if not _name.startswith("_"):
            globals()[_name] = getattr(mod, _name)
            if _name not in __all__:
                __all__.append(_name)

for _sub in ("preserved_functions", "golden_agent_core", "status_listener", "monolith"):
    try:
        _mod = __import__(f"golden_agent.{_sub}", fromlist=["*"])
        _export_module(_mod)
    except Exception:
        pass
