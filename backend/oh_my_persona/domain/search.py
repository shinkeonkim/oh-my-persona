import re
from dataclasses import dataclass, field
from typing import Any, Protocol

TOKEN = re.compile(r"[0-9A-Za-z가-힣][0-9A-Za-z가-힣_.+#-]*")
KOREAN_SUFFIXES = (
    "에서는",
    "으로부터",
    "에게서",
    "까지",
    "부터",
    "에서",
    "으로",
    "에게",
    "께서",
    "처럼",
    "보다",
    "은",
    "는",
    "이",
    "가",
    "을",
    "를",
    "의",
    "에",
    "와",
    "과",
    "도",
    "로",
)


@dataclass(frozen=True, slots=True)
class SearchHit:
    chunk_id: str
    text: str
    score: float
    source_id: str | None = None
    title: str | None = None
    url: str | None = None
    published_at: str | None = None
    observed_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class Retriever(Protocol):
    def search(self, query: str, limit: int = 6) -> list[SearchHit]: ...


def tokenize(text: str) -> list[str]:
    output: list[str] = []
    for raw in TOKEN.findall(text):
        token = raw.lower()
        output.append(token)
        if any("가" <= character <= "힣" for character in token) and len(token) >= 3:
            output.extend(token[index : index + 3] for index in range(len(token) - 2))
        for suffix in KOREAN_SUFFIXES:
            if token.endswith(suffix) and len(token) > len(suffix) + 1:
                output.append(token[: -len(suffix)])
                break
    return output
