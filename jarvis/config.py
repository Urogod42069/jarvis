"""Configuration loaded from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = os.environ.get("JARVIS_MODEL", "claude-sonnet-4-5-20250929")
DB_PATH = Path(os.environ.get("JARVIS_DB_PATH", "") or Path.home() / ".jarvis" / "conversations.db")
LOG_LEVEL = os.environ.get("JARVIS_LOG_LEVEL", "INFO")

SYSTEM_PROMPT = """\
You are Jarvis, a personal AI assistant. You are helpful, direct, and efficient.

Guidelines:
- Be concise. Don't pad responses with filler.
- When you need to take an action (read a file, run a command, etc.), \
use the available tools rather than asking the user to do it.
- Always explain what you're about to do before doing it.
- If a tool call could have side effects, propose the action and wait for confirmation.
"""


def validate() -> None:
    """Raise if required config is missing."""
    if not ANTHROPIC_API_KEY:
        raise SystemExit(
            "ANTHROPIC_API_KEY is not set. "
            "Copy .env.example to .env and fill in your key."
        )
