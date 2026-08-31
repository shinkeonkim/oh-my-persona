import hashlib
import json
import os

from fastapi import HTTPException, Request

from .schemas import KnowledgeRequest


def sse(event: str, data: object) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def enforce_rate_limit(request: Request, limiter: object) -> None:
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


def knowledge_values(request: KnowledgeRequest) -> dict[str, object]:
    return {
        "title": request.title,
        "content": request.content,
        "source_url": str(request.source_url),
        "observed_at": request.observed_at.isoformat() if request.observed_at else None,
        "status": request.status,
    }


def gap_summary(questions: list[dict]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for question in questions:
        status = question["status"]
        summary[status] = summary.get(status, 0) + 1
    return summary


def packaged_chunk(chunk: dict, source: dict) -> dict:
    return {
        "id": chunk["chunk_id"],
        "chunk_id": chunk["chunk_id"],
        "document_id": chunk.get("document_id"),
        "source_id": chunk.get("source_id"),
        "title": source.get("title") or chunk.get("source_path", "packaged chunk"),
        "content": chunk["text"],
        "source_path": chunk.get("source_path"),
        "source_url": chunk.get("canonical_url") or source.get("canonical_url"),
        "published_at": source.get("published_at"),
        "observed_at": chunk.get("observed_at") or source.get("observed_at"),
        "content_sha256": chunk.get("content_sha256"),
        "ordinal": chunk.get("ordinal"),
        "status": "packaged",
        "managed": False,
    }
