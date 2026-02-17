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


def _print_history(db: Database, conversation_id: str) -> None:
    """Print prior messages from a resumed conversation."""
    msgs = db.get_messages(conversation_id)
    for msg in msgs:
        if msg.role == "user" and msg.content:
            console.print(f"[bold cyan]You:[/bold cyan] {msg.content}")
        elif msg.role == "assistant" and msg.content:
            console.print(Panel(Markdown(msg.content), title="Jarvis", border_style="dim blue"))
    if msgs:
        console.print("[dim]--- end of history ---[/dim]\n")


def _resume_conversation(db: Database) -> str | None:
    """Show recent conversations and let the user pick one. Returns conversation id or None."""
    convos = db.list_conversations(limit=10)
    if not convos:
        console.print("[dim]No previous conversations found.[/dim]")
        return None

    console.print("\n[bold]Recent conversations:[/bold]")
    for i, c in enumerate(convos, 1):
        msg_count = db.message_count(c["id"])
        console.print(
            f"  [bold]{i}.[/bold] {c['id']}  "
            f"[dim]{c['updated_at'][:16]}[/dim]  "
            f"{c['title']}  [dim]({msg_count} msgs)[/dim]"
        )

    while True:
        choice = console.input("\n[yellow]Enter number or conversation ID (or 'c' to cancel): [/yellow]").strip()
        if choice.lower() == "c":
            return None
        # Try as a number index
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(convos):
                return convos[idx]["id"]
        except ValueError:
            pass
        # Try as a conversation ID
        if db.get_conversation(choice):
            return choice
        console.print("[dim]Invalid choice. Try again.[/dim]")


def main() -> None:
    config.validate()

    db = Database(config.DB_PATH)

    # Start a new conversation each session
    conversation_id = db.create_conversation(title="CLI session")
    agent = Agent(db, conversation_id)

    console.print(Panel(
        "[bold green]Jarvis[/bold green] is ready. Type your message below.\n"
        "Commands: [dim]/quit[/dim]  [dim]/history[/dim]  [dim]/resume[/dim]  [dim]/new[/dim]",
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
                    msg_count = db.message_count(c["id"])
                    console.print(
                        f"  {c['id']}  [dim]{c['updated_at'][:16]}[/dim]  "
                        f"{c['title']}  [dim]({msg_count} msgs)[/dim]"
                    )
                continue

            if user_input.lower().startswith("/resume"):
                parts = user_input.split(maxsplit=1)
                if len(parts) == 2 and db.get_conversation(parts[1].strip()):
                    cid = parts[1].strip()
                else:
                    cid = _resume_conversation(db)
                if cid:
                    conversation_id = cid
                    agent = Agent(db, conversation_id)
                    convo = db.get_conversation(conversation_id)
                    console.print(f"\n[green]Resumed conversation [bold]{conversation_id}[/bold][/green]")
                    _print_history(db, conversation_id)
                continue

            if user_input.lower() == "/new":
                conversation_id = db.create_conversation(title="CLI session")
                agent = Agent(db, conversation_id)
                console.print(f"[green]Started new conversation [bold]{conversation_id}[/bold][/green]")
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
