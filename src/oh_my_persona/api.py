from __future__ import annotations

import asyncio
import json
import os
import secrets
from contextlib import asynccontextmanager
from threading import Event

from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .agent import ALLOWED_MODELS
from .conversations import ConversationStore, RateLimiter
from .corpus import read_jsonl
from .discord_bridge import DiscordBridge
from .presentation.http_support import (
    enforce_rate_limit,
    gap_summary,
    knowledge_values,
    packaged_chunk,
    sse,
)
from .presentation.schemas import (
    AdminConversationMessageRequest,
    ChatRequest,
    KnowledgeGapAnswerRequest,
    KnowledgeGapQuestionRequest,
    KnowledgeRequest,
    WidgetChatRequest,
)
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


@asynccontextmanager
async def lifespan(_: FastAPI):
    await asyncio.to_thread(store.initialize)
    await asyncio.to_thread(knowledge_store.initialize)
    await asyncio.to_thread(knowledge_question_store.initialize)
    yield


app = FastAPI(title="oh-my-persona", version="0.2.0", lifespan=lifespan)
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


def require_admin(authorization: str | None = Header(default=None)) -> None:
    expected = os.environ.get("PERSONA_ADMIN_TOKEN")
    supplied = authorization.removeprefix("Bearer ") if authorization else ""
    if not expected:
        raise HTTPException(status_code=503, detail="admin access is not configured")
    if not secrets.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="invalid admin token")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(
        FRONTEND_DIST / "index.html" if FRONTEND_DIST.is_dir() else STATIC / "index.html"
    )


@app.get("/admin", include_in_schema=False)
def admin_index():
    return FileResponse(
        FRONTEND_DIST / "index.html" if FRONTEND_DIST.is_dir() else STATIC / "admin.html"
    )


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
    sources = read_jsonl(root_path() / "data/registry/sources.jsonl")
    source = next((item for item in sources if item["source_id"] == source_id), None)
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
            current_messages = await asyncio.to_thread(store.messages, conversation_id)
            serialized = json.dumps(current_messages, ensure_ascii=False, sort_keys=True)
            if serialized != previous:
                previous = serialized
                idle_ticks = 0
                yield sse("messages", {"messages": current_messages})
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
    return {
        "conversation_id": request.conversation_id,
        "answer": response,
        "sources": sources,
    }


@app.get("/api/conversations/{conversation_id}")
def get_conversation(conversation_id: str):
    if not store.exists(conversation_id):
        raise HTTPException(status_code=404, detail="conversation not found")
    return {"conversation_id": conversation_id, "messages": store.messages(conversation_id)}


@app.get("/api/admin/knowledge")
def admin_knowledge(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    packaged_limit: int = Query(50, ge=1, le=200),
    packaged_offset: int = Query(0, ge=0),
    q: str | None = Query(None, max_length=200),
    source_id: str | None = Query(None, max_length=100),
    _: None = Depends(require_admin),
):
    managed = knowledge_store.list(limit, offset)
    chunks = read_jsonl(root_path() / "data/processed/chunks.jsonl")
    sources = {
        item["source_id"]: item for item in read_jsonl(root_path() / "data/registry/sources.jsonl")
    }
    query = (q or "").casefold()
    filtered = [
        item
        for item in chunks
        if (not source_id or item.get("source_id") == source_id)
        and (
            not query
            or query
            in " ".join(
                (
                    item.get("text", ""),
                    item.get("source_path", ""),
                    item.get("source_id", ""),
                    item.get("document_id", ""),
                )
            ).casefold()
        )
    ]
    packaged = [
        packaged_chunk(item, sources.get(item.get("source_id", ""), {}))
        for item in filtered[packaged_offset : packaged_offset + packaged_limit]
    ]
    facets = sorted(
        {
            (item.get("source_id"), sources.get(item.get("source_id", ""), {}).get("title"))
            for item in chunks
            if item.get("source_id")
        }
    )
    return {
        "managed": managed,
        "packaged": packaged,
        "packaged_total": len(filtered),
        "packaged_unfiltered_total": len(chunks),
        "packaged_offset": packaged_offset,
        "packaged_limit": packaged_limit,
        "source_facets": [{"source_id": key, "title": title} for key, title in facets],
    }


@app.get("/api/admin/chunks/{chunk_id}")
def admin_chunk(chunk_id: str, _: None = Depends(require_admin)):
    chunk = next(
        (
            item
            for item in read_jsonl(root_path() / "data/processed/chunks.jsonl")
            if item["chunk_id"] == chunk_id
        ),
        None,
    )
    if not chunk:
        raise HTTPException(status_code=404, detail="chunk not found")
    source = next(
        (
            item
            for item in read_jsonl(root_path() / "data/registry/sources.jsonl")
            if item["source_id"] == chunk.get("source_id")
        ),
        {},
    )
    return packaged_chunk(chunk, source)


@app.post("/api/admin/knowledge", status_code=201)
def create_admin_knowledge(request: KnowledgeRequest, _: None = Depends(require_admin)):
    return knowledge_store.create(knowledge_values(request))


@app.put("/api/admin/knowledge/{item_id}")
def update_admin_knowledge(
    item_id: str,
    request: KnowledgeRequest,
    _: None = Depends(require_admin),
):
    item = knowledge_store.update(item_id, knowledge_values(request))
    if not item:
        raise HTTPException(status_code=404, detail="knowledge not found")
    return item


@app.delete("/api/admin/knowledge/{item_id}", status_code=204)
def delete_admin_knowledge(item_id: str, _: None = Depends(require_admin)):
    if not knowledge_store.delete(item_id):
        raise HTTPException(status_code=404, detail="knowledge not found")


@app.get("/api/admin/knowledge-gaps")
def admin_knowledge_gaps(_: None = Depends(require_admin)):
    path = root_path() / "data/processed/knowledge-gaps.json"
    if not path.is_file():
        raise HTTPException(status_code=503, detail="knowledge gap report is not packaged")
    report = json.loads(path.read_text(encoding="utf-8"))
    managed = knowledge_store.list(500, 0)
    answers = {
        item["title"].split("]", 1)[0].removeprefix("["): item
        for item in managed
        if item["title"].startswith("[") and "]" in item["title"]
    }
    custom = [
        {
            **item,
            "status": "empty",
            "priority": 3,
            "evidence_count": 0,
            "unique_source_count": 0,
            "source_ids": [],
            "evidence_urls": [],
            "answer_hint": "새로 만든 질문입니다. 시점, 판단 이유, 행동, 결과를 직접 답변하세요.",
            "custom": True,
        }
        for item in knowledge_question_store.list()
    ]
    questions = []
    for question in [*custom, *report["questions"]]:
        item = answers.get(question["question_id"])
        questions.append(
            {
                **question,
                "status": (
                    "direct_answer"
                    if item and item["status"] == "active"
                    else "draft_answer"
                    if item
                    else question["status"]
                ),
                "managed_answer": item,
            }
        )
    return {"summary": gap_summary(questions), "questions": questions}


@app.post("/api/admin/knowledge-gaps/questions", status_code=201)
def create_admin_knowledge_gap_question(
    request: KnowledgeGapQuestionRequest,
    _: None = Depends(require_admin),
):
    return knowledge_question_store.create(request.model_dump())


@app.delete("/api/admin/knowledge-gaps/questions/{question_id}", status_code=204)
def delete_admin_knowledge_gap_question(question_id: str, _: None = Depends(require_admin)):
    if not knowledge_question_store.delete(question_id):
        raise HTTPException(status_code=404, detail="question not found")


@app.post("/api/admin/knowledge-gaps/{question_id}/answer")
def answer_admin_knowledge_gap(
    question_id: str,
    request: KnowledgeGapAnswerRequest,
    _: None = Depends(require_admin),
):
    questions = {
        item["question_id"]: item
        for item in read_jsonl(root_path() / "data/questionnaires/persona-questions.jsonl")
    }
    custom = knowledge_question_store.get(question_id)
    if custom:
        questions[question_id] = custom
    question = questions.get(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="question not found")
    evidence = [str(url) for url in request.evidence_urls]
    content = (
        f"질문: {question['question']}\n\n답변일: {request.answered_at.isoformat()}\n\n"
        f"답변: {request.answer.strip()}\n\n"
        f"참고 URL: {', '.join(evidence) if evidence else '없음'}"
    )
    existing = next(
        (
            item
            for item in knowledge_store.list(500, 0)
            if item["title"].startswith(f"[{question_id}]")
        ),
        None,
    )
    item_id = existing["id"] if existing else None
    values = {
        "title": f"[{question_id}] {question['question']}",
        "content": content,
        "source_url": (
            f"https://persona.shinkeonkim.com/api/knowledge/{item_id}"
            if item_id
            else "https://persona.shinkeonkim.com/"
        ),
        "observed_at": request.answered_at.isoformat(),
        "status": "active" if request.visibility == "public" else "draft",
    }
    if existing:
        return knowledge_store.update(existing["id"], values)
    created = knowledge_store.create(values)
    values["source_url"] = f"https://persona.shinkeonkim.com/api/knowledge/{created['id']}"
    return knowledge_store.update(created["id"], values)


@app.get("/api/admin/conversations")
def admin_conversations(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _: None = Depends(require_admin),
):
    return {"conversations": store.list_conversations(limit, offset)}


@app.get("/api/admin/conversations/{conversation_id}")
def admin_conversation(conversation_id: str, _: None = Depends(require_admin)):
    if not store.exists(conversation_id):
        raise HTTPException(status_code=404, detail="conversation not found")
    return {"conversation_id": conversation_id, "messages": store.messages(conversation_id, 500)}


@app.post("/api/admin/conversations/{conversation_id}/messages", status_code=201)
def admin_conversation_message(
    conversation_id: str,
    request: AdminConversationMessageRequest,
    _: None = Depends(require_admin),
):
    if not store.exists(conversation_id):
        raise HTTPException(status_code=404, detail="conversation not found")
    store.append(conversation_id, "owner", request.content.strip())
    return store.messages(conversation_id, 1)[0]


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
        cancel_signal = Event()
        try:
            fallback, sources = await asyncio.to_thread(answer_context, request.message, history)
            yield sse("conversation", {"conversation_id": conversation_id})
            yield sse("sources", sources)
            chunks: list[str] = []
            if fallback is not None:
                chunks.append(fallback)
                yield sse("token", {"text": fallback})
            else:
                from .agent import stream_invoke

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
        except Exception as error:  # noqa: BLE001 - stream needs a structured terminal event
            yield sse("error", {"message": str(error)})

    return StreamingResponse(
        events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"}
    )


def _enforce_rate_limit(request: Request) -> None:
    enforce_rate_limit(request, limiter)
