from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from ....domain.repositories import KnowledgeQuestionRepository, KnowledgeRepository
from ....infrastructure.files import read_jsonl
from ...http_support import gap_summary
from ...schemas import KnowledgeGapAnswerRequest, KnowledgeGapQuestionRequest


def create_gap_admin_router(
    root: Path,
    knowledge: KnowledgeRepository,
    questions: KnowledgeQuestionRepository,
) -> APIRouter:
    router = APIRouter()

    @router.get("/knowledge-gaps")
    def list_gaps() -> dict[str, Any]:
        path = root / "data/processed/knowledge-gaps.json"
        if not path.is_file():
            raise HTTPException(status_code=503, detail="knowledge gap report is not packaged")
        report = json.loads(path.read_text(encoding="utf-8"))
        answers = {
            item["title"].split("]", 1)[0].removeprefix("["): item
            for item in knowledge.list(500, 0)
            if item["title"].startswith("[") and "]" in item["title"]
        }
        custom = [_custom_question(item) for item in questions.list()]
        rows = [
            _with_managed_answer(question, answers) for question in [*custom, *report["questions"]]
        ]
        return {"summary": gap_summary(rows), "questions": rows}

    @router.post("/knowledge-gaps/questions", status_code=201)
    def create_gap(request: KnowledgeGapQuestionRequest) -> dict[str, Any]:
        return questions.create(request.model_dump())

    @router.delete("/knowledge-gaps/questions/{question_id}", status_code=204)
    def delete_gap(question_id: str) -> None:
        if not questions.delete(question_id):
            raise HTTPException(status_code=404, detail="question not found")

    @router.post("/knowledge-gaps/{question_id}/answer")
    def answer_gap(question_id: str, request: KnowledgeGapAnswerRequest) -> dict[str, Any] | None:
        indexed = {
            item["question_id"]: item
            for item in read_jsonl(root / "data/questionnaires/persona-questions.jsonl")
        }
        custom = questions.get(question_id)
        if custom:
            indexed[question_id] = custom
        question = indexed.get(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="question not found")
        existing = next(
            (
                item
                for item in knowledge.list(500, 0)
                if item["title"].startswith(f"[{question_id}]")
            ),
            None,
        )
        item_id = existing["id"] if existing else None
        values = _answer_values(question_id, question, request, item_id)
        if existing:
            return knowledge.update(existing["id"], values)
        created = knowledge.create(values)
        values["source_url"] = f"https://persona.shinkeonkim.com/api/knowledge/{created['id']}"
        return knowledge.update(created["id"], values)

    return router


def _custom_question(item: dict[str, Any]) -> dict[str, Any]:
    return {
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


def _with_managed_answer(
    question: dict[str, Any], answers: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    item = answers.get(question["question_id"])
    status = (
        "direct_answer"
        if item and item["status"] == "active"
        else "draft_answer"
        if item
        else question["status"]
    )
    return {**question, "status": status, "managed_answer": item}


def _answer_values(
    question_id: str,
    question: dict[str, Any],
    request: KnowledgeGapAnswerRequest,
    item_id: str | None,
) -> dict[str, Any]:
    evidence = [str(url) for url in request.evidence_urls]
    content = (
        f"질문: {question['question']}\n\n답변일: {request.answered_at.isoformat()}\n\n"
        f"답변: {request.answer.strip()}\n\n"
        f"참고 URL: {', '.join(evidence) if evidence else '없음'}"
    )
    return {
        "title": f"[{question_id}] {question['question']}",
        "content": content,
        "source_url": f"https://persona.shinkeonkim.com/api/knowledge/{item_id}"
        if item_id
        else "https://persona.shinkeonkim.com/",
        "observed_at": request.answered_at.isoformat(),
        "status": "active" if request.visibility == "public" else "draft",
    }
