"""FastAPI composition root.

Routes live in the presentation package; this module owns process-wide
dependencies so the historical `oh_my_persona.api:app` entrypoint stays stable.
"""

from __future__ import annotations

import asyncio
import json
import os
import secrets
from contextlib import asynccontextmanager
from threading import Event

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .agent import ALLOWED_MODELS, stream_invoke
from .application import ChatUseCase
from .conversations import ConversationStore, RateLimiter
from .corpus import read_jsonl
from .discord_bridge import DiscordBridge
from .presentation.admin_router import create_admin_router
from .presentation.http_support import enforce_rate_limit, sse
from .presentation.schemas import ChatRequest, WidgetChatRequest
from .service import (
    answer,
    answer_context,
    knowledge_question_store,
    knowledge_store,
    root_path,
    search,
)
from .sessions import create_widget_session, verify_widget_session

ROOT = root_path()
STATIC = ROOT / "static"
FRONTEND_DIST = ROOT / "frontend" / "dist"
store = ConversationStore()
limiter = RateLimiter(store)
discord_bridge = DiscordBridge(store)
chat_use_case = ChatUseCase(store, answer)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await asyncio.to_thread(store.initialize)
    await asyncio.to_thread(knowledge_store.initialize)
    await asyncio.to_thread(knowledge_question_store.initialize)
    yield


def require_admin(authorization: str | None = Header(default=None)) -> None:
    expected = os.environ.get("PERSONA_ADMIN_TOKEN")
    supplied = authorization.removeprefix("Bearer ") if authorization else ""
    if not expected:
        raise HTTPException(status_code=503, detail="admin access is not configured")
    if not secrets.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="invalid admin token")


app = FastAPI(title="oh-my-persona", version="0.3.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://portfolio.shinkeonkim.com",
        "https://resume.shinkeonkim.com",
        "http://localhost:4173",
        "http://localhost:5173",
    ],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Persona-Session-Token"],
)
app.mount("/static", StaticFiles(directory=STATIC), name="static")
if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="frontend-assets")
app.include_router(
    create_admin_router(
        root=ROOT,
        knowledge_store=knowledge_store,
        question_store=knowledge_question_store,
        conversation_store=store,
        authenticate=require_admin,
    )
)


def _spa_or_fallback(name: str) -> FileResponse:
    target = FRONTEND_DIST / "index.html" if FRONTEND_DIST.is_dir() else STATIC / name
    return FileResponse(target)


@app.get("/", include_in_schema=False)
def index():
    return _spa_or_fallback("index.html")


@app.get("/admin", include_in_schema=False)
def admin_index():
    return _spa_or_fallback("admin.html")


@app.get("/sdk/persona-widget.js", include_in_schema=False)
def widget_sdk():
    return FileResponse(
        STATIC / "persona-widget.js",
        media_type="text/javascript",
        headers={"Cache-Control": "no-cache, must-revalidate"},
    )


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
    source = next(
        (
            item
            for item in read_jsonl(ROOT / "data/registry/sources.jsonl")
            if item["source_id"] == source_id
        ),
        None,
    )
    if not source or source.get("status") not in {"accepted", "review"}:
        raise HTTPException(status_code=404, detail="source not found")
    return source


@app.get("/api/knowledge/{item_id}")
def public_managed_knowledge(item_id: str):
    item = knowledge_store.get(item_id)
    if not item or item["status"] != "active":
        raise HTTPException(status_code=404, detail="knowledge not found")
    return item


@app.post("/api/conversations", status_code=201)
def create_conversation():
    return {"conversation_id": store.create()}


@app.get("/api/conversations/{conversation_id}")
def get_conversation(conversation_id: str):
    if not store.exists(conversation_id):
        raise HTTPException(status_code=404, detail="conversation not found")
    return {"conversation_id": conversation_id, "messages": store.messages(conversation_id)}


@app.post("/api/widget/sessions", status_code=201)
def create_widget_session_api(request: Request):
    conversation_id, token = create_widget_session(store, request.headers.get("origin"))
    return {"conversation_id": conversation_id, "token": token}


@app.get("/api/widget/conversations/{conversation_id}")
def get_widget_conversation(conversation_id: str, x_persona_session_token: str = Header()):
    if not verify_widget_session(store, conversation_id, x_persona_session_token):
        raise HTTPException(status_code=401, detail="invalid widget session")
    return {"conversation_id": conversation_id, "messages": store.messages(conversation_id)}


@app.get("/api/widget/conversations/{conversation_id}/stream")
async def stream_widget_conversation(
    conversation_id: str,
    http_request: Request,
    x_persona_session_token: str = Header(),
):
    if not verify_widget_session(store, conversation_id, x_persona_session_token):
        raise HTTPException(status_code=401, detail="invalid widget session")

    async def events():
        previous = json.dumps(store.messages(conversation_id), ensure_ascii=False, sort_keys=True)
        idle_ticks = 0
        yield sse("ready", {"conversation_id": conversation_id})
        while not await http_request.is_disconnected():
            await asyncio.sleep(2)
            messages = await asyncio.to_thread(store.messages, conversation_id)
            serialized = json.dumps(messages, ensure_ascii=False, sort_keys=True)
            if serialized != previous:
                previous, idle_ticks = serialized, 0
                yield sse("messages", {"messages": messages})
            else:
                idle_ticks += 1
                if idle_ticks >= 7:
                    idle_ticks = 0
                    yield ": keepalive\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/widget/chat")
def widget_chat(request: WidgetChatRequest, http_request: Request, background: BackgroundTasks):
    _enforce_rate_limit(http_request)
    if not verify_widget_session(store, request.conversation_id, request.token):
        raise HTTPException(status_code=401, detail="invalid widget session")
    history = store.messages(request.conversation_id, 20)
    try:
        response, sources = answer(request.message, request.model, history)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    store.append(request.conversation_id, "user", request.message)
    store.append(request.conversation_id, "assistant", response, request.model, sources)
    background.add_task(
        discord_bridge.mirror_exchange,
        request.conversation_id,
        request.message,
        response,
        http_request.headers.get("origin"),
    )
    return {"conversation_id": request.conversation_id, "answer": response, "sources": sources}


@app.post("/api/chat")
def chat(request: ChatRequest, http_request: Request):
    _enforce_rate_limit(http_request)
    try:
        result = chat_use_case.execute(request.message, request.model, request.conversation_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {
        "conversation_id": result.conversation_id,
        "answer": result.answer,
        "sources": result.sources,
    }


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest, http_request: Request):
    _enforce_rate_limit(http_request)
    conversation_id = request.conversation_id or store.create()
    if not store.exists(conversation_id):
        raise HTTPException(status_code=404, detail="conversation not found")
    history = store.messages(conversation_id, 20)

    async def events():
        cancel_signal, chunks = Event(), []
        try:
            fallback, sources = await asyncio.to_thread(answer_context, request.message, history)
            yield sse("conversation", {"conversation_id": conversation_id})
            yield sse("sources", sources)
            if fallback is not None:
                chunks.append(fallback)
                yield sse("token", {"text": fallback})
            else:
                async with asyncio.timeout(45):
                    async for token in stream_invoke(
                        request.message, sources, request.model, history, cancel_signal
                    ):
                        if await http_request.is_disconnected():
                            cancel_signal.set()
                            return
                        chunks.append(token)
                        yield sse("token", {"text": token})
            response = "".join(chunks)
            await asyncio.to_thread(store.append, conversation_id, "user", request.message)
            await asyncio.to_thread(
                store.append, conversation_id, "assistant", response, request.model, sources
            )
            yield sse("done", {})
        except TimeoutError:
            cancel_signal.set()
            yield sse("error", {"message": "답변 시간이 45초를 초과했습니다. 다시 시도해주세요."})
        except Exception as error:  # noqa: BLE001
            yield sse("error", {"message": str(error)})

    return StreamingResponse(
        events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"}
    )


def _enforce_rate_limit(request: Request) -> None:
    enforce_rate_limit(request, limiter)
