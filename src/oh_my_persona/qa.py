from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from .corpus import read_jsonl
from .ingest import SENSITIVE_PATTERNS


def build_answers(root: Path, answers_path: Path) -> dict[str, int]:
    questions = {
        item["question_id"]: item
        for item in read_jsonl(root / "data/questionnaires/persona-questions.jsonl")
    }
    answers = read_jsonl(answers_path)
    sections: list[str] = ["# 김신건 직접 답변\n"]
    accepted = skipped = 0
    for item in answers:
        question = questions.get(item.get("question_id"))
        answer = " ".join(str(item.get("answer", "")).split())
        if not question:
            raise ValueError(f"unknown question_id: {item.get('question_id')}")
        if item.get("visibility") != "public" or not answer:
            skipped += 1
            continue
        findings = [name for name, pattern in SENSITIVE_PATTERNS.items() if pattern.search(answer)]
        if findings:
            raise ValueError(f"{item['question_id']}: sensitive material detected: {findings}")
        evidence = [url for url in item.get("evidence_urls", []) if url.startswith("https://")]
        sections.append(
            f"## {item['question_id']}\n\n질문: {question['question']}\n\n"
            f"답변일: {item.get('answered_at') or '날짜 미상'}\n\n답변: {answer}\n\n"
            f"참고 URL: {', '.join(evidence) if evidence else '없음'}\n"
        )
        accepted += 1
    content = "\n".join(sections)
    output = root / "data/curated/persona-interview-answers.md"
    output.write_text(content, encoding="utf-8")
    digest = hashlib.sha256(content.encode()).hexdigest()
    manifest = root / "data/registry/documents.jsonl"
    records = [item for item in read_jsonl(manifest) if item.get("source_id") != "SRC-0015"]
    records.append({
        "document_id": f"DOC-{digest[:20]}", "source_id": "SRC-0015",
        "canonical_url": "https://github.com/shinkeonkim/oh-my-persona/blob/main/data/curated/persona-interview-answers.md",
        "repository_url": "https://github.com/shinkeonkim/oh-my-persona",
        "commit_sha": None, "relative_path": "persona-interview-answers.md",
        "raw_path": "data/curated/persona-interview-answers.md", "content_sha256": digest,
        "mime_type": "text/markdown", "observed_at": datetime.now(UTC).isoformat(),
        "extractor_version": "persona-interview-v1", "status": "accepted",
    })
    records.sort(key=lambda item: (item["source_id"], item["relative_path"]))
    manifest.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in records), encoding="utf-8")
    return {"accepted": accepted, "skipped": skipped}
