"""Framework-independent persona domain types."""

from .entities import ConversationMessage, Knowledge, MessageRole, SourceReference
from .ingestion import InboxFinding, InboxStatus
from .search import SearchHit

__all__ = [
    "ConversationMessage",
    "InboxFinding",
    "InboxStatus",
    "Knowledge",
    "MessageRole",
    "SearchHit",
    "SourceReference",
]
