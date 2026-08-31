from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal

MessageRole = Literal["user", "assistant", "owner"]
KnowledgeStatus = Literal["active", "draft"]


@dataclass(frozen=True, slots=True)
class SourceReference:
    source_id: str | None = None
    title: str | None = None
    url: str | None = None
    published_at: str | None = None
    observed_at: str | None = None


@dataclass(frozen=True, slots=True)
class ConversationMessage:
    role: MessageRole
    content: str
    model: str | None = None
    sources: tuple[SourceReference, ...] = field(default_factory=tuple)
    created_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class Knowledge:
    id: str
    title: str
    content: str
    source_url: str
    status: KnowledgeStatus
    observed_at: date | None = None
