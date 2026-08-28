from __future__ import annotations

import os
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path

from .retrieval import MemoryRetriever

PRIVATE_QUERY_TERMS = ("주민등록번호", "전화번호", "집주소", "비밀번호", "API 키", "private key")


def root_path() -> Path:
    configured = os.environ.get("PERSONA_ROOT")
    return Path(configured).resolve() if configured else Path.cwd().resolve()


@lru_cache(maxsize=1)
def retriever():
    return MemoryRetriever(root_path())


def search(query: str, limit: int = 6) -> list[dict]:
    return [asdict(hit) for hit in retriever().search(query, limit)]


def grounded_fallback(question: str, hits: list[dict]) -> str:
    if not hits:
        return "현재 공개 자료에서는 이 질문에 답할 근거를 찾지 못했습니다."
    lines = ["확인된 자료를 기준으로 정리하면 다음과 같습니다."]
    for index, hit in enumerate(hits[:4], 1):
        excerpt = " ".join(hit["text"].split())[:260]
        lines.append(f"[{index}] {excerpt}")
    lines.append("이는 검색된 자료의 발췌이며, 해석이 필요한 부분은 원출처와 시점을 함께 확인해야 합니다.")
    return "\n\n".join(lines)


def answer(question: str, model_alias: str | None = None) -> tuple[str, list[dict]]:
    if any(term.lower() in question.lower() for term in PRIVATE_QUERY_TERMS):
        return "개인정보나 인증정보는 공개 자료 검색 및 답변 대상에서 제외합니다.", []
    hits = search(question)
    if not hits or not os.environ.get("PERSONA_LITELLM_URL") or not os.environ.get("PERSONA_LITELLM_KEY"):
        return grounded_fallback(question, hits), hits
    from .agent import invoke
    return invoke(question, hits, model_alias), hits
