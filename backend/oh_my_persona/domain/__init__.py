"""Framework-independent persona domain types."""

from .chunks import Chunk
from .entities import ConversationMessage, Knowledge, MessageRole, SourceReference
from .ingestion import InboxFinding, InboxStatus
from .search import SearchHit

__all__ = [
    "Chunk",
    "ConversationMessage",
    "InboxFinding",
    "InboxStatus",
    "Knowledge",
    "MessageRole",
    "SearchHit",
    "SourceReference",
]
