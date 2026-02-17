"""Data models for messages and tool calls."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Message:
    role: str  # "user" | "assistant"
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[ToolResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ToolCall:
    tool_name: str
    tool_input: dict[str, Any]
    call_id: str = ""


@dataclass
class ToolResult:
    call_id: str
    output: str
    is_error: bool = False
