from __future__ import annotations

import asyncio
import hashlib
import json
import os
import secrets
from contextlib import asynccontextmanager
from datetime import date

from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import AnyHttpUrl, BaseModel, Field

from .agent import ALLOWED_MODELS
from .conversations import ConversationStore, RateLimiter
from .corpus import read_jsonl
from .discord_bridge import DiscordBridge
from .service import answer, knowledge_store, root_path, search
from .sessions import create_widget_session, verify_widget_session

ROOT = root_path()
STATIC = ROOT / "static"
store = ConversationStore()
limiter = RateLimiter(store)
discord_bridge = DiscordBridge(store)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await asyncio.to_thread(store.initialize)
    await asyncio.to_thread(knowledge_store.initialize)
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


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    model: str | None = None
    conversation_id: str | None = None


class WidgetChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str
    token: str = Field(min_length=20, max_length=200)
    model: str | None = None


class KnowledgeRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=50_000)
    source_url: AnyHttpUrl
    observed_at: date | None = None
    status: str = Field(pattern="^(active|draft)$")


class AdminConversationMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class KnowledgeGapAnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=50_000)
    answered_at: date
    visibility: str = Field(pattern="^(private|public)$")
    evidence_urls: list[AnyHttpUrl] = Field(default_factory=list, max_length=20)


def require_admin(authorization: str | None = Header(default=None)) -> None:
    expected = os.environ.get("PERSONA_ADMIN_TOKEN")
    supplied = authorization.removeprefix("Bearer ") if authorization else ""
    if not expected:
        raise HTTPException(status_code=503, detail="admin access is not configured")
    if not secrets.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="invalid admin token")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/admin", include_in_schema=False)
def admin_index():
    return FileResponse(STATIC / "admin.html")


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
        yield _sse("ready", {"conversation_id": conversation_id})
        while not await http_request.is_disconnected():
            await asyncio.sleep(2)
            current_messages = await asyncio.to_thread(store.messages, conversation_id)
            serialized = json.dumps(current_messages, ensure_ascii=False, sort_keys=True)
            if serialized != previous:
                previous = serialized
                idle_ticks = 0
                yield _sse("messages", {"messages": current_messages})
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
    limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0),
    _: None = Depends(require_admin),
):
    managed = knowledge_store.list(limit, offset)
    chunks = read_jsonl(root_path() / "data/processed/chunks.jsonl")
    packaged = [{
        "id": item["chunk_id"], "title": item.get("source_path", "packaged chunk"),
        "content": item["text"], "source_url": item.get("canonical_url"),
        "observed_at": item.get("observed_at"), "status": "packaged", "managed": False,
    } for item in chunks[offset : offset + limit]]
    return {"managed": managed, "packaged": packaged, "packaged_total": len(chunks)}


@app.post("/api/admin/knowledge", status_code=201)
def create_admin_knowledge(request: KnowledgeRequest, _: None = Depends(require_admin)):
    return knowledge_store.create(_knowledge_values(request))


@app.put("/api/admin/knowledge/{item_id}")
def update_admin_knowledge(
    item_id: str, request: KnowledgeRequest, _: None = Depends(require_admin),
):
    item = knowledge_store.update(item_id, _knowledge_values(request))
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
        for item in managed if item["title"].startswith("[PQ-") and "]" in item["title"]
    }
    questions = []
    for question in report["questions"]:
        item = answers.get(question["question_id"])
        questions.append({
            **question,
            "status": (
                "direct_answer" if item and item["status"] == "active"
                else "draft_answer" if item else question["status"]
            ),
            "managed_answer": item,
        })
    return {"summary": _gap_summary(questions), "questions": questions}


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
    question = questions.get(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="question not found")
    evidence = [str(url) for url in request.evidence_urls]
    content = (
        f"질문: {question['question']}\n\n답변일: {request.answered_at.isoformat()}\n\n"
        f"답변: {request.answer.strip()}\n\n"
        f"참고 URL: {', '.join(evidence) if evidence else '없음'}"
    )
    values = {
        "title": f"[{question_id}] {question['question']}",
        "content": content,
        "source_url": (
            "https://github.com/shinkeonkim/oh-my-persona/blob/main/"
            f"data/curated/persona-interview-answers.md#{question_id.lower()}"
        ),
        "observed_at": request.answered_at.isoformat(),
        "status": "active" if request.visibility == "public" else "draft",
    }
    existing = next(
        (item for item in knowledge_store.list(500, 0) if item["title"].startswith(f"[{question_id}]")),
        None,
    )
    return knowledge_store.update(existing["id"], values) if existing else knowledge_store.create(values)


@app.get("/api/admin/conversations")
def admin_conversations(
    limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0),
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


def _knowledge_values(request: KnowledgeRequest) -> dict:
    return {
        "title": request.title,
        "content": request.content,
        "source_url": str(request.source_url),
        "observed_at": request.observed_at.isoformat() if request.observed_at else None,
        "status": request.status,
    }


def _gap_summary(questions: list[dict]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for question in questions:
        status = question["status"]
        summary[status] = summary.get(status, 0) + 1
    return summary
