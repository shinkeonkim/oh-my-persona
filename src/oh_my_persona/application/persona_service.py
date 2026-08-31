from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict
from typing import Any

from ..domain.privacy import PRIVATE_QUERY_TERMS
from ..domain.repositories import KnowledgeRepository
from ..domain.search import SearchHit
from .knowledge.retrieval import MemoryRetriever, tokenize

AnswerGenerator = Callable[
    [str, list[dict[str, Any]], str | None, list[dict[str, Any]] | None],
    tuple[str, list[dict[str, Any]]],
]


class PersonaService:
    """Search and answer use cases independent of storage and model providers."""

    def __init__(
        self,
        retriever: MemoryRetriever,
        knowledge_repository: KnowledgeRepository,
        answer_generator: AnswerGenerator | None = None,
    ) -> None:
        self._retriever = retriever
        self._knowledge_repository = knowledge_repository
        self._answer_generator = answer_generator

    def search(self, query: str, limit: int = 6) -> list[dict[str, Any]]:
        hits = self._retriever.search(query, limit)
        query_terms = set(tokenize(query))
        for item in self._knowledge_repository.active():
            matches = query_terms.intersection(tokenize(f"{item['title']} {item['content']}"))
            if matches:
                hits.append(_managed_hit(item, len(matches)))
        hits.sort(key=lambda hit: -hit.score)
        return [asdict(hit) for hit in hits[:limit]]

    def answer(
        self,
        question: str,
        model_alias: str | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> tuple[str, list[dict[str, Any]]]:
        fallback, hits = self.answer_context(question, history)
        if fallback is not None:
            return fallback, hits
        if self._answer_generator is None:
            return grounded_fallback(hits), hits
        return self._answer_generator(question, hits, model_alias, history)

    def answer_context(
        self, question: str, history: list[dict[str, Any]] | None = None
    ) -> tuple[str | None, list[dict[str, Any]]]:
        if _is_private_query(question):
            return "개인정보나 인증정보는 공개 자료 검색 및 답변 대상에서 제외합니다.", []
        recent = " ".join(
            item["content"] for item in (history or [])[-6:] if item.get("role") == "user"
        )
        hits = self.search(f"{recent} {question}".strip())
        if not hits or self._answer_generator is None:
            return grounded_fallback(hits), hits
        return None, hits


def grounded_fallback(hits: list[dict[str, Any]]) -> str:
    if not hits:
        return "제가 공개한 자료에서는 이 질문에 답할 근거를 찾지 못했습니다."
    lines = ["제가 공개한 자료를 기준으로 말씀드리겠습니다."]
    for index, hit in enumerate(hits[:4], 1):
        excerpt = " ".join(hit["text"].split())[:260]
        lines.append(f"[{index}] {excerpt}")
    lines.append(
        "검색된 자료의 발췌이므로, 해석이 필요한 부분은 원출처와 시점을 함께 확인해 주세요."
    )
    return "\n\n".join(lines)


def _is_private_query(question: str) -> bool:
    normalized = question.lower()
    return any(term.lower() in normalized for term in PRIVATE_QUERY_TERMS)


def _managed_hit(item: dict[str, Any], match_count: int) -> SearchHit:
    return SearchHit(
        chunk_id=f"ADMIN-{item['id']}",
        text=item["content"],
        score=float(match_count * 100),
        source_id="ADMIN",
        title=item["title"],
        url=item["source_url"],
        observed_at=item.get("observed_at"),
        metadata={"managed": True, "knowledge_id": item["id"]},
    )
