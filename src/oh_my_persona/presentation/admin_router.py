"""Administrative HTTP endpoints.

The router translates HTTP DTOs only. Persistence remains behind the injected
stores, which makes the boundary explicit and independently testable.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from ..corpus import read_jsonl
from .http_support import gap_summary, knowledge_values, packaged_chunk
from .schemas import (
    AdminConversationMessageRequest,
    KnowledgeGapAnswerRequest,
    KnowledgeGapQuestionRequest,
    KnowledgeRequest,
)


def create_admin_router(
    *,
    root: Any,
    knowledge_store: Any,
    question_store: Any,
    conversation_store: Any,
    authenticate: Callable[..., None],
) -> APIRouter:
    router = APIRouter(prefix="/api/admin", dependencies=[Depends(authenticate)])

    @router.get("/knowledge")
    def list_knowledge(
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        packaged_limit: int = Query(50, ge=1, le=200),
        packaged_offset: int = Query(0, ge=0),
        q: str | None = Query(None, max_length=200),
        source_id: str | None = Query(None, max_length=100),
    ):
        chunks = read_jsonl(root / "data/processed/chunks.jsonl")
        sources = {
            item["source_id"]: item for item in read_jsonl(root / "data/registry/sources.jsonl")
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
        facets = sorted(
            {
                (item.get("source_id"), sources.get(item.get("source_id", ""), {}).get("title"))
                for item in chunks
                if item.get("source_id")
            }
        )
        return {
            "managed": knowledge_store.list(limit, offset),
            "packaged": [
                packaged_chunk(item, sources.get(item.get("source_id", ""), {}))
                for item in filtered[packaged_offset : packaged_offset + packaged_limit]
            ],
            "packaged_total": len(filtered),
            "packaged_unfiltered_total": len(chunks),
            "packaged_offset": packaged_offset,
            "packaged_limit": packaged_limit,
            "source_facets": [{"source_id": key, "title": title} for key, title in facets],
        }

    @router.get("/chunks/{chunk_id}")
    def get_chunk(chunk_id: str):
        chunk = next(
            (
                item
                for item in read_jsonl(root / "data/processed/chunks.jsonl")
                if item["chunk_id"] == chunk_id
            ),
            None,
        )
        if not chunk:
            raise HTTPException(status_code=404, detail="chunk not found")
        source = next(
            (
                item
                for item in read_jsonl(root / "data/registry/sources.jsonl")
                if item["source_id"] == chunk.get("source_id")
            ),
            {},
        )
        return packaged_chunk(chunk, source)

    @router.post("/knowledge", status_code=201)
    def create_knowledge(request: KnowledgeRequest):
        return knowledge_store.create(knowledge_values(request))

    @router.put("/knowledge/{item_id}")
    def update_knowledge(item_id: str, request: KnowledgeRequest):
        item = knowledge_store.update(item_id, knowledge_values(request))
        if not item:
            raise HTTPException(status_code=404, detail="knowledge not found")
        return item

    @router.delete("/knowledge/{item_id}", status_code=204)
    def delete_knowledge(item_id: str):
        if not knowledge_store.delete(item_id):
            raise HTTPException(status_code=404, detail="knowledge not found")

    @router.get("/knowledge-gaps")
    def list_gaps():
        path = root / "data/processed/knowledge-gaps.json"
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
            for item in question_store.list()
        ]
        questions = []
        for question in [*custom, *report["questions"]]:
            item = answers.get(question["question_id"])
            questions.append(
                {
                    **question,
                    "status": "direct_answer"
                    if item and item["status"] == "active"
                    else "draft_answer"
                    if item
                    else question["status"],
                    "managed_answer": item,
                }
            )
        return {"summary": gap_summary(questions), "questions": questions}

    @router.post("/knowledge-gaps/questions", status_code=201)
    def create_gap(request: KnowledgeGapQuestionRequest):
        return question_store.create(request.model_dump())

    @router.delete("/knowledge-gaps/questions/{question_id}", status_code=204)
    def delete_gap(question_id: str):
        if not question_store.delete(question_id):
            raise HTTPException(status_code=404, detail="question not found")

    @router.post("/knowledge-gaps/{question_id}/answer")
    def answer_gap(question_id: str, request: KnowledgeGapAnswerRequest):
        questions = {
            item["question_id"]: item
            for item in read_jsonl(root / "data/questionnaires/persona-questions.jsonl")
        }
        custom = question_store.get(question_id)
        if custom:
            questions[question_id] = custom
        question = questions.get(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="question not found")
        evidence = [str(url) for url in request.evidence_urls]
        content = f"질문: {question['question']}\n\n답변일: {request.answered_at.isoformat()}\n\n답변: {request.answer.strip()}\n\n참고 URL: {', '.join(evidence) if evidence else '없음'}"
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
            "source_url": f"https://persona.shinkeonkim.com/api/knowledge/{item_id}"
            if item_id
            else "https://persona.shinkeonkim.com/",
            "observed_at": request.answered_at.isoformat(),
            "status": "active" if request.visibility == "public" else "draft",
        }
        if existing:
            return knowledge_store.update(existing["id"], values)
        created = knowledge_store.create(values)
        values["source_url"] = f"https://persona.shinkeonkim.com/api/knowledge/{created['id']}"
        return knowledge_store.update(created["id"], values)

    @router.get("/conversations")
    def conversations(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
        return {"conversations": conversation_store.list_conversations(limit, offset)}

    @router.get("/conversations/{conversation_id}")
    def conversation(conversation_id: str):
        if not conversation_store.exists(conversation_id):
            raise HTTPException(status_code=404, detail="conversation not found")
        return {
            "conversation_id": conversation_id,
            "messages": conversation_store.messages(conversation_id, 500),
        }

    @router.post("/conversations/{conversation_id}/messages", status_code=201)
    def reply(conversation_id: str, request: AdminConversationMessageRequest):
        if not conversation_store.exists(conversation_id):
            raise HTTPException(status_code=404, detail="conversation not found")
        conversation_store.append(conversation_id, "owner", request.content.strip())
        return conversation_store.messages(conversation_id, 1)[0]

    return router
