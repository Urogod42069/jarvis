"""FastAPI server — REST + SSE interface for Jarvis."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from . import config
from .agent import Agent
from .database import Database

# ---------------------------------------------------------------------------
# Lifespan — open/close the shared database
# ---------------------------------------------------------------------------

db: Database | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global db
    config.validate()
    db = Database(config.DB_PATH)
    yield
    if db:
        db.close()


app = FastAPI(title="Jarvis API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Pydantic request / response schemas
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str
    stream: bool = False


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str


class ConversationOut(BaseModel):
    id: str
    title: str
    updated_at: str
    message_count: int = 0


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: str


# ---------------------------------------------------------------------------
# Routes — Conversations
# ---------------------------------------------------------------------------


@app.get("/api/conversations", response_model=list[ConversationOut])
def list_conversations(limit: int = 20):
    assert db is not None
    convos = db.list_conversations(limit=limit)
    return [
        ConversationOut(
            id=c["id"],
            title=c["title"],
            updated_at=c["updated_at"],
            message_count=db.message_count(c["id"]),
        )
        for c in convos
    ]


@app.post("/api/conversations", response_model=ConversationOut)
def create_conversation(title: str = ""):
    assert db is not None
    cid = db.create_conversation(title=title or "API session")
    convo = db.get_conversation(cid)
    assert convo is not None
    return ConversationOut(
        id=convo["id"],
        title=convo["title"],
        updated_at=convo["updated_at"],
        message_count=0,
    )


@app.get("/api/conversations/{conversation_id}", response_model=ConversationOut)
def get_conversation(conversation_id: str):
    assert db is not None
    convo = db.get_conversation(conversation_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationOut(
        id=convo["id"],
        title=convo["title"],
        updated_at=convo["updated_at"],
        message_count=db.message_count(convo["id"]),
    )


@app.get("/api/conversations/{conversation_id}/messages", response_model=list[MessageOut])
def get_messages(conversation_id: str):
    assert db is not None
    if not db.get_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    msgs = db.get_messages(conversation_id)
    return [
        MessageOut(
            role=m.role,
            content=m.content,
            created_at=m.created_at.isoformat(),
        )
        for m in msgs
        if m.content  # skip empty tool-result messages
    ]


# ---------------------------------------------------------------------------
# Routes — Chat
# ---------------------------------------------------------------------------


@app.post("/api/conversations/{conversation_id}/chat")
def chat(conversation_id: str, req: ChatRequest):
    assert db is not None
    if not db.get_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")

    agent = Agent(db, conversation_id)

    if req.stream:
        return StreamingResponse(
            _stream_reply(agent, req.message),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # Non-streaming: tools auto-approved for API usage (no confirmation)
    reply = agent.chat(req.message)
    return ChatResponse(reply=reply, conversation_id=conversation_id)


async def _stream_reply(agent: Agent, message: str) -> AsyncGenerator[str, None]:
    """Run the synchronous agent.chat in a thread and yield SSE chunks."""
    chunks: asyncio.Queue[str | None] = asyncio.Queue()

    def stream_fn(chunk: str) -> None:
        chunks.put_nowait(chunk)

    async def run_agent():
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: agent.chat(message, stream_fn=stream_fn))
        await chunks.put(None)  # sentinel

    task = asyncio.create_task(run_agent())

    while True:
        chunk = await chunks.get()
        if chunk is None:
            yield "data: [DONE]\n\n"
            break
        # Escape newlines for SSE
        yield f"data: {chunk}\n\n"

    await task


# ---------------------------------------------------------------------------
# Convenience endpoint — one-shot (creates conversation automatically)
# ---------------------------------------------------------------------------


@app.post("/api/chat", response_model=ChatResponse)
def chat_oneshot(req: ChatRequest):
    assert db is not None
    cid = db.create_conversation(title="API session")
    agent = Agent(db, cid)

    if req.stream:
        return StreamingResponse(
            _stream_reply(agent, req.message),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    reply = agent.chat(req.message)
    return ChatResponse(reply=reply, conversation_id=cid)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    import uvicorn

    config.validate()
    host = "0.0.0.0"
    port = int(__import__("os").environ.get("JARVIS_API_PORT", "8000"))
    print(f"Starting Jarvis API on {host}:{port}")
    uvicorn.run("jarvis.api:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
