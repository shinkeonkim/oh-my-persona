from dataclasses import dataclass, field
from typing import Any


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
