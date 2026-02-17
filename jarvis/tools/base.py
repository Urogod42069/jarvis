"""Abstract base class for Jarvis tools."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """Every tool must implement name, description, parameters, and execute."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool name (snake_case)."""

    @property
    @abstractmethod
    def description(self) -> str:
        """One-line description shown to the model."""

    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        """JSON Schema for the tool's input parameters."""

    @property
    def requires_confirmation(self) -> bool:
        """If True, the agent will ask for user confirmation before executing."""
        return False

    @abstractmethod
    def execute(self, **kwargs: Any) -> str:
        """Run the tool and return a string result (or raise)."""

    def definition(self) -> dict[str, Any]:
        """Anthropic tool-use definition."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }
