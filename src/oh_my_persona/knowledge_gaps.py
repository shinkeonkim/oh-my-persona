from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .corpus import read_jsonl
from .retrieval import MemoryRetriever


def analyze_knowledge_gaps(root: Path, limit: int = 8) -> dict:
    """Rank interview questions by how weakly the current corpus can answer them."""
    questions = read_jsonl(root / "data/questionnaires/persona-questions.jsonl")
    retriever = MemoryRetriever(root)
    rows = []
    for question in questions:
        hits = retriever.search(question["question"], limit)
        cited = [hit for hit in hits if hit.source_id and hit.url]
        source_ids = sorted({hit.source_id for hit in cited if hit.source_id})
        direct = [
            hit for hit in cited
            if hit.metadata.get("source_path", "").endswith("persona-interview-answers.md")
        ]
        if direct:
            status, priority = "direct_answer", 0
        elif not cited:
            status, priority = "empty", 3
        elif len(source_ids) == 1:
            status, priority = "single_source", 2
        else:
            status, priority = "indirect_evidence", 1
        rows.append({
            **question,
            "status": status,
            "priority": priority,
            "evidence_count": len(cited),
            "unique_source_count": len(source_ids),
            "source_ids": source_ids,
            "evidence_urls": list(dict.fromkeys(hit.url for hit in cited if hit.url))[:5],
            "answer_hint": _answer_hint(question, status),
        })
    rows.sort(key=lambda item: (
        -item["priority"], item["unique_source_count"], item["evidence_count"],
        item["category"], item["question_id"],
    ))
    return {
        "summary": dict(Counter(row["status"] for row in rows)),
        "questions": rows,
    }


def write_knowledge_gap_outputs(root: Path, output: Path, template: Path) -> dict:
    report = analyze_knowledge_gaps(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    unanswered = [item for item in report["questions"] if item["status"] != "direct_answer"]
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text("".join(
        json.dumps({
            "question_id": item["question_id"],
            "answer": "",
            "answered_at": "YYYY-MM-DD",
            "visibility": "private",
            "evidence_urls": item["evidence_urls"],
        }, ensure_ascii=False) + "\n"
        for item in unanswered
    ), encoding="utf-8")
    return {"questions": len(report["questions"]), "unanswered": len(unanswered), **report["summary"]}


def _answer_hint(question: dict, status: str) -> str:
    scope = question.get("time_scope", "날짜 미상")
    if status == "empty":
        return f"{scope}의 구체적 사건, 본인의 판단, 행동, 결과를 먼저 기록하세요."
    if status == "single_source":
        return f"{scope}의 직접 답변을 작성하고 가능한 경우 독립적인 공개 URL을 하나 더 연결하세요."
    if status == "indirect_evidence":
        return f"기존 자료를 반복하지 말고 {scope} 당시의 이유와 현재 관점의 차이를 직접 설명하세요."
    return "직접 답변이 있으므로 날짜나 관점이 바뀌었을 때만 갱신하세요."
