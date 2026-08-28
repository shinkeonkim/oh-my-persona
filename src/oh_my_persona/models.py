from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class InboxFinding:
    path: str
    status: Literal["accepted", "rejected", "review"]
    sha256: str
    mime: str
    reasons: tuple[str, ...] = ()
