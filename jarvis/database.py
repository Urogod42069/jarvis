"""SQLite-backed conversation history."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .models import Message, ToolCall, ToolResult


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


class Database:
    def __init__(self, db_path: Path) -> None:
        _ensure_dir(db_path)
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self._migrate()

    def _migrate(self) -> None:
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL REFERENCES conversations(id),
                role TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                tool_calls TEXT NOT NULL DEFAULT '[]',
                tool_results TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_messages_conversation
                ON messages(conversation_id, id);
        """)
        self.conn.commit()

    # -- conversations --

    def create_conversation(self, title: str = "") -> str:
        cid = uuid.uuid4().hex[:12]
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (cid, title, now, now),
        )
        self.conn.commit()
        return cid

    def list_conversations(self, limit: int = 20) -> list[dict]:
        rows = self.conn.execute(
            "SELECT id, title, updated_at FROM conversations ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    # -- messages --

    def add_message(self, conversation_id: str, msg: Message) -> None:
        self.conn.execute(
            """INSERT INTO messages (conversation_id, role, content, tool_calls, tool_results, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                conversation_id,
                msg.role,
                msg.content,
                json.dumps([{"tool_name": tc.tool_name, "tool_input": tc.tool_input, "call_id": tc.call_id} for tc in msg.tool_calls]),
                json.dumps([{"call_id": tr.call_id, "output": tr.output, "is_error": tr.is_error} for tr in msg.tool_results]),
                msg.created_at.isoformat(),
            ),
        )
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (now, conversation_id),
        )
        self.conn.commit()

    def get_messages(self, conversation_id: str) -> list[Message]:
        rows = self.conn.execute(
            "SELECT role, content, tool_calls, tool_results, created_at FROM messages WHERE conversation_id = ? ORDER BY id",
            (conversation_id,),
        ).fetchall()
        messages: list[Message] = []
        for r in rows:
            messages.append(Message(
                role=r["role"],
                content=r["content"],
                tool_calls=[ToolCall(**tc) for tc in json.loads(r["tool_calls"])],
                tool_results=[ToolResult(**tr) for tr in json.loads(r["tool_results"])],
                created_at=datetime.fromisoformat(r["created_at"]),
            ))
        return messages

    def close(self) -> None:
        self.conn.close()
