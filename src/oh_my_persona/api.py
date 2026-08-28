from __future__ import annotations

import asyncio
import hashlib
import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .agent import ALLOWED_MODELS
from .conversations import ConversationStore, RateLimiter
from .corpus import read_jsonl
from .service import answer, root_path, search

ROOT = root_path()
STATIC = ROOT / "static"
store = ConversationStore()
limiter = RateLimiter(store)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await asyncio.to_thread(store.initialize)
    yield


app = FastAPI(title="oh-my-persona", version="0.2.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    model: str | None = None
    conversation_id: str | None = None


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/models")
def models() -> dict[str, tuple[str, ...]]:
    return {"models": ALLOWED_MODELS}


@app.get("/api/search")
def search_api(q: str = Query(min_length=1, max_length=4000), limit: int = Query(6, ge=1, le=20)):
    return {"query": q, "hits": search(q, limit)}


@app.get("/api/sources/{source_id}")
def source_api(source_id: str):
    sources = read_jsonl(root_path() / "data/registry/sources.jsonl")
    source = next((item for item in sources if item["source_id"] == source_id), None)
    if not source or source.get("status") not in {"accepted", "review"}:
        raise HTTPException(status_code=404, detail="source not found")
    return source


@app.post("/api/conversations", status_code=201)
def create_conversation():
    return {"conversation_id": store.create()}


@app.get("/api/conversations/{conversation_id}")
def get_conversation(conversation_id: str):
    if not store.exists(conversation_id):
        raise HTTPException(status_code=404, detail="conversation not found")
    return {"conversation_id": conversation_id, "messages": store.messages(conversation_id)}


@app.post("/api/chat")
def chat(request: ChatRequest, http_request: Request):
    _enforce_rate_limit(http_request)
    conversation_id = request.conversation_id or store.create()
    if not store.exists(conversation_id):
        raise HTTPException(status_code=404, detail="conversation not found")
    history = store.messages(conversation_id, 20)
    try:
        response, sources = answer(request.message, request.model, history)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    store.append(conversation_id, "user", request.message)
    store.append(conversation_id, "assistant", response, request.model, sources)
    return {"conversation_id": conversation_id, "answer": response, "sources": sources}


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest, http_request: Request):
    _enforce_rate_limit(http_request)
    conversation_id = request.conversation_id or store.create()
    if not store.exists(conversation_id):
        raise HTTPException(status_code=404, detail="conversation not found")
    history = store.messages(conversation_id, 20)

    async def events():
        try:
            response, sources = await asyncio.to_thread(
                answer, request.message, request.model, history
            )
            await asyncio.to_thread(store.append, conversation_id, "user", request.message)
            await asyncio.to_thread(
                store.append, conversation_id, "assistant", response, request.model, sources
            )
            yield _sse("conversation", {"conversation_id": conversation_id})
            yield _sse("sources", sources)
            for token in response.splitlines(keepends=True):
                yield _sse("token", {"text": token})
            yield _sse("done", {})
        except Exception as error:  # noqa: BLE001 - stream needs a structured terminal event
            yield _sse("error", {"message": str(error)})
    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


def _sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _enforce_rate_limit(request: Request) -> None:
    client_ip = request.headers.get("cf-connecting-ip") or (
        request.client.host if request.client else "unknown"
    )
    salt = os.environ.get("PERSONA_RATE_LIMIT_SALT", "persona-public")
    identity = hashlib.sha256(f"{salt}:{client_ip}".encode()).hexdigest()
    allowed, retry_after = limiter.consume(identity)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="시간당 AI 질문 한도를 초과했습니다. 잠시 후 다시 시도해주세요.",
            headers={"Retry-After": str(retry_after)},
        )
