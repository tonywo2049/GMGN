from __future__ import annotations

from importlib import import_module
from typing import Any, List


__all__ = [
    "DEFAULT_FOLLOW_WINDOW",
    "SCHEMA_VERSION",
    "SOURCE",
    "build_report",
    "main",
    "render_human",
]


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(name)
    module = import_module(".report", __name__)
    return getattr(module, name)


def __dir__() -> List[str]:
    return sorted(__all__)
