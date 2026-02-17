"""CLI entry point for Jarvis."""

from __future__ import annotations

import json
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from . import config
from .agent import Agent
from .database import Database
from .models import ToolCall

console = Console()


def confirm_action(tc: ToolCall) -> bool:
    """Print a proposed action and ask the user for y/n confirmation."""
    console.print()
    console.print(Panel(
        Text.from_markup(
            f"[bold]Tool:[/bold] {tc.tool_name}\n"
            f"[bold]Input:[/bold] {json.dumps(tc.tool_input, indent=2)}"
        ),
        title="[yellow]Action Proposed[/yellow]",
        border_style="yellow",
    ))
    while True:
        answer = console.input("[yellow]Allow this action? (y/n): [/yellow]").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        console.print("[dim]Please enter y or n.[/dim]")


def main() -> None:
    config.validate()

    db = Database(config.DB_PATH)

    # Start a new conversation each session (or extend later to resume)
    conversation_id = db.create_conversation(title="CLI session")
    agent = Agent(db, conversation_id)

    console.print(Panel(
        "[bold green]Jarvis[/bold green] is ready. Type your message below.\n"
        "Commands: [dim]/quit[/dim] to exit, [dim]/history[/dim] to list conversations.",
        border_style="green",
    ))

    try:
        while True:
            try:
                user_input = console.input("[bold cyan]You:[/bold cyan] ").strip()
            except EOFError:
                break

            if not user_input:
                continue

            if user_input.lower() in ("/quit", "/exit", "/q"):
                break

            if user_input.lower() == "/history":
                for c in db.list_conversations():
                    console.print(f"  {c['id']}  {c['updated_at']}  {c['title']}")
                continue

            with console.status("[bold green]Thinking...[/bold green]"):
                try:
                    reply = agent.chat(user_input, confirm_fn=confirm_action)
                except KeyboardInterrupt:
                    console.print("\n[dim]Interrupted.[/dim]")
                    continue

            console.print()
            console.print(Panel(Markdown(reply), title="Jarvis", border_style="blue"))
            console.print()

    except KeyboardInterrupt:
        pass
    finally:
        db.close()
        console.print("\n[dim]Goodbye.[/dim]")


if __name__ == "__main__":
    main()
