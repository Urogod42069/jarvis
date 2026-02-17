"""Tool: read a local file and return its contents."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import Tool

MAX_SIZE_BYTES = 256 * 1024  # 256 KB safety limit


class ReadFileTool(Tool):
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a local file. Returns the text content."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to read.",
                },
            },
            "required": ["path"],
        }

    @property
    def requires_confirmation(self) -> bool:
        return True

    def execute(self, *, path: str) -> str:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return f"Error: file not found — {p}"
        if not p.is_file():
            return f"Error: not a regular file — {p}"
        if p.stat().st_size > MAX_SIZE_BYTES:
            return f"Error: file too large ({p.stat().st_size:,} bytes, limit {MAX_SIZE_BYTES:,})"
        try:
            return p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return f"Error: file is not valid UTF-8 — {p}"
