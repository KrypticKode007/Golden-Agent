"""
Golden-Agent (Project Kai-007) Core Package.

Automatically exposes primary engine components from `monolith`
and preserved fallback utilities from `preserved_functions`.
"""

__version__ = "1.0.0"
__author__ = "KrypticKode007"

__all__ = []

# 1. Load preserved fallback classes and functions first
try:
    from . import preserved_functions as _preserved

    for _name in dir(_preserved):
        if not _name.startswith("_"):
            globals()[_name] = getattr(_preserved, _name)
            if _name not in __all__:
                __all__.append(_name)
except ImportError:
    pass

# 2. Load primary engine (overrides preserved items with active versions)
try:
    from . import monolith as _monolith

    for _name in dir(_monolith):
        if not _name.startswith("_"):
            globals()[_name] = getattr(_monolith, _name)
            if _name not in __all__:
                __all__.append(_name)
except ImportError:
    pass
  
