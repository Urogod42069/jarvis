"""Tool: write content to a local file."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import Tool

MAX_SIZE_BYTES = 256 * 1024  # 256 KB safety limit


class WriteFileTool(Tool):
    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return (
            "Write text content to a local file. Creates parent directories if needed. "
            "Overwrites existing files. Use for creating or editing files."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to write.",
                },
                "content": {
                    "type": "string",
                    "description": "The text content to write to the file.",
                },
            },
            "required": ["path", "content"],
        }

    @property
    def requires_confirmation(self) -> bool:
        return True

    def execute(self, *, path: str, content: str) -> str:
        if len(content.encode("utf-8")) > MAX_SIZE_BYTES:
            return f"Error: content too large (limit {MAX_SIZE_BYTES:,} bytes)"

        p = Path(path).expanduser().resolve()

        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        except OSError as exc:
            return f"Error writing file: {exc}"

        return f"Wrote {len(content):,} characters to {p}"
