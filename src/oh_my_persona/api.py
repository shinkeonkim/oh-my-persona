from __future__ import annotations

import asyncio
import json

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .agent import ALLOWED_MODELS
from .corpus import read_jsonl
from .service import answer, root_path, search

ROOT = root_path()
STATIC = ROOT / "static"
app = FastAPI(title="oh-my-persona", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    model: str | None = None


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


@app.post("/api/chat")
def chat(request: ChatRequest):
    try:
        response, sources = answer(request.message, request.model)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"answer": response, "sources": sources}


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    async def events():
        try:
            response, sources = await asyncio.to_thread(answer, request.message, request.model)
            yield _sse("sources", sources)
            for token in response.splitlines(keepends=True):
                yield _sse("token", {"text": token})
            yield _sse("done", {})
        except Exception as error:  # noqa: BLE001 - stream needs a structured terminal event
            yield _sse("error", {"message": str(error)})
    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


def _sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
