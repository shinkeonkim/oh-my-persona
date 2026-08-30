from __future__ import annotations

import os
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path

from .admin import KnowledgeStore
from .models import SearchHit
from .retrieval import MemoryRetriever, tokenize

PRIVATE_QUERY_TERMS = ("주민등록번호", "전화번호", "집주소", "비밀번호", "API 키", "private key")
knowledge_store = KnowledgeStore(os.environ.get("PERSONA_DATABASE_URL"))


def root_path() -> Path:
    configured = os.environ.get("PERSONA_ROOT")
    return Path(configured).resolve() if configured else Path.cwd().resolve()


@lru_cache(maxsize=1)
def retriever():
    return MemoryRetriever(root_path())


def search(query: str, limit: int = 6) -> list[dict]:
    hits = retriever().search(query, limit)
    query_terms = set(tokenize(query))
    for item in knowledge_store.active():
        matches = query_terms.intersection(tokenize(f"{item['title']} {item['content']}"))
        if not matches:
            continue
        hits.append(SearchHit(
            chunk_id=f"ADMIN-{item['id']}", text=item["content"],
            score=float(len(matches) * 100), source_id="ADMIN", title=item["title"],
            url=item["source_url"], observed_at=item.get("observed_at"),
            metadata={"managed": True, "knowledge_id": item["id"]},
        ))
    hits.sort(key=lambda hit: -hit.score)
    return [asdict(hit) for hit in hits[:limit]]


def grounded_fallback(question: str, hits: list[dict]) -> str:
    if not hits:
        return "제가 공개한 자료에서는 이 질문에 답할 근거를 찾지 못했습니다."
    lines = ["제가 공개한 자료를 기준으로 말씀드리겠습니다."]
    for index, hit in enumerate(hits[:4], 1):
        excerpt = " ".join(hit["text"].split())[:260]
        lines.append(f"[{index}] {excerpt}")
    lines.append("검색된 자료의 발췌이므로, 해석이 필요한 부분은 원출처와 시점을 함께 확인해 주세요.")
    return "\n\n".join(lines)


def answer(question: str, model_alias: str | None = None,
           history: list[dict] | None = None) -> tuple[str, list[dict]]:
    if any(term.lower() in question.lower() for term in PRIVATE_QUERY_TERMS):
        return "개인정보나 인증정보는 공개 자료 검색 및 답변 대상에서 제외합니다.", []
    recent_user_context = " ".join(
        item["content"] for item in (history or [])[-6:] if item.get("role") == "user"
    )
    retrieval_query = f"{recent_user_context} {question}".strip()
    hits = search(retrieval_query)
    if not hits or not os.environ.get("PERSONA_LITELLM_URL") or not os.environ.get("PERSONA_LITELLM_KEY"):
        return grounded_fallback(question, hits), hits
    from .agent import invoke
    return invoke(question, hits, model_alias, history), hits
