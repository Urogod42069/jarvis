"""Core agent: manages the conversation loop and tool execution."""

from __future__ import annotations

from typing import Any

import anthropic

from . import config
from .database import Database
from .models import Message, ToolCall, ToolResult
from .tools import get_tool, tool_definitions


class Agent:
    def __init__(self, db: Database, conversation_id: str) -> None:
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.db = db
        self.conversation_id = conversation_id

    # -- public API --

    def chat(self, user_text: str, *, confirm_fn: ConfirmFn | None = None) -> str:
        """Send user text, handle tool calls, return final assistant text."""
        self.db.add_message(
            self.conversation_id,
            Message(role="user", content=user_text),
        )

        messages = self._build_messages()
        return self._run_loop(messages, confirm_fn=confirm_fn)

    # -- internals --

    def _build_messages(self) -> list[dict[str, Any]]:
        """Convert stored messages to Anthropic API format."""
        api_msgs: list[dict[str, Any]] = []
        for msg in self.db.get_messages(self.conversation_id):
            if msg.role == "user" and msg.tool_results:
                # This is a tool_result turn
                content: list[dict[str, Any]] = []
                for tr in msg.tool_results:
                    content.append({
                        "type": "tool_result",
                        "tool_use_id": tr.call_id,
                        "content": tr.output,
                        **({"is_error": True} if tr.is_error else {}),
                    })
                api_msgs.append({"role": "user", "content": content})
            elif msg.role == "assistant" and msg.tool_calls:
                # Assistant turn with tool use blocks
                content = []
                if msg.content:
                    content.append({"type": "text", "text": msg.content})
                for tc in msg.tool_calls:
                    content.append({
                        "type": "tool_use",
                        "id": tc.call_id,
                        "name": tc.tool_name,
                        "input": tc.tool_input,
                    })
                api_msgs.append({"role": "assistant", "content": content})
            else:
                api_msgs.append({"role": msg.role, "content": msg.content})
        return api_msgs

    def _run_loop(
        self,
        messages: list[dict[str, Any]],
        *,
        confirm_fn: ConfirmFn | None = None,
    ) -> str:
        """Call the API in a loop until the model stops using tools."""
        while True:
            response = self.client.messages.create(
                model=config.MODEL,
                max_tokens=4096,
                system=config.SYSTEM_PROMPT,
                tools=tool_definitions(),
                messages=messages,
            )

            # Extract text and tool_use blocks
            text_parts: list[str] = []
            tool_calls: list[ToolCall] = []

            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)
                elif block.type == "tool_use":
                    tool_calls.append(ToolCall(
                        tool_name=block.name,
                        tool_input=block.input,
                        call_id=block.id,
                    ))

            assistant_text = "\n".join(text_parts)

            # Save assistant message
            self.db.add_message(
                self.conversation_id,
                Message(role="assistant", content=assistant_text, tool_calls=tool_calls),
            )

            if response.stop_reason != "tool_use" or not tool_calls:
                return assistant_text

            # Execute tools
            tool_results = self._execute_tools(tool_calls, confirm_fn=confirm_fn)

            # Save tool results as a user message
            self.db.add_message(
                self.conversation_id,
                Message(role="user", content="", tool_results=tool_results),
            )

            # Rebuild messages for next iteration
            messages = self._build_messages()

    def _execute_tools(
        self,
        tool_calls: list[ToolCall],
        *,
        confirm_fn: ConfirmFn | None = None,
    ) -> list[ToolResult]:
        results: list[ToolResult] = []
        for tc in tool_calls:
            tool = get_tool(tc.tool_name)
            if tool is None:
                results.append(ToolResult(
                    call_id=tc.call_id,
                    output=f"Error: unknown tool '{tc.tool_name}'",
                    is_error=True,
                ))
                continue

            # Action proposal: ask for confirmation if the tool requires it
            if tool.requires_confirmation and confirm_fn:
                approved = confirm_fn(tc)
                if not approved:
                    results.append(ToolResult(
                        call_id=tc.call_id,
                        output="Action was denied by user.",
                        is_error=True,
                    ))
                    continue

            try:
                output = tool.execute(**tc.tool_input)
            except Exception as exc:
                output = f"Error executing {tc.tool_name}: {exc}"
                results.append(ToolResult(call_id=tc.call_id, output=output, is_error=True))
                continue

            results.append(ToolResult(call_id=tc.call_id, output=output))

        return results


# Type alias for the confirmation callback
from typing import Callable
ConfirmFn = Callable[[ToolCall], bool]
