"""Tool registry — auto-discovers tool modules in this package."""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import Any

from .base import Tool

_registry: dict[str, Tool] = {}


def _discover() -> None:
    """Import every module in jarvis/tools/ and register Tool subclasses."""
    package_dir = Path(__file__).parent
    for info in pkgutil.iter_modules([str(package_dir)]):
        if info.name == "base":
            continue
        module = importlib.import_module(f".{info.name}", package=__package__)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, Tool)
                and attr is not Tool
            ):
                instance = attr()
                _registry[instance.name] = instance


def get_all_tools() -> dict[str, Tool]:
    if not _registry:
        _discover()
    return dict(_registry)


def get_tool(name: str) -> Tool | None:
    if not _registry:
        _discover()
    return _registry.get(name)


def tool_definitions() -> list[dict[str, Any]]:
    """Return Anthropic-formatted tool definitions for all registered tools."""
    return [tool.definition() for tool in get_all_tools().values()]
