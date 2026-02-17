"""Tool: run a shell command and return its output."""

from __future__ import annotations

import subprocess
from typing import Any

from .base import Tool

TIMEOUT_SECONDS = 30
MAX_OUTPUT_BYTES = 64 * 1024  # 64 KB


class RunShellTool(Tool):
    @property
    def name(self) -> str:
        return "run_shell"

    @property
    def description(self) -> str:
        return (
            "Run a shell command and return its stdout and stderr. "
            "Use for system tasks like listing files, checking disk usage, "
            "running scripts, git commands, etc. "
            "Commands time out after 30 seconds."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute (passed to /bin/sh -c).",
                },
                "working_directory": {
                    "type": "string",
                    "description": "Optional working directory for the command. Defaults to the current directory.",
                },
            },
            "required": ["command"],
        }

    @property
    def requires_confirmation(self) -> bool:
        return True

    def execute(self, *, command: str, working_directory: str | None = None) -> str:
        try:
            result = subprocess.run(
                ["sh", "-c", command],
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                cwd=working_directory,
            )
        except subprocess.TimeoutExpired:
            return f"Error: command timed out after {TIMEOUT_SECONDS}s"
        except OSError as exc:
            return f"Error: {exc}"

        parts: list[str] = []
        if result.stdout:
            parts.append(result.stdout)
        if result.stderr:
            parts.append(f"[stderr]\n{result.stderr}")
        if result.returncode != 0:
            parts.append(f"[exit code: {result.returncode}]")

        output = "\n".join(parts) if parts else "(no output)"

        if len(output) > MAX_OUTPUT_BYTES:
            output = output[:MAX_OUTPUT_BYTES] + f"\n... (truncated at {MAX_OUTPUT_BYTES:,} bytes)"

        return output
