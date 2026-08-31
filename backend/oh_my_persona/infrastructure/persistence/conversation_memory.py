from __future__ import annotations

import threading
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any


class MemoryConversationStore:
    def __init__(self) -> None:
        self.database_url: None = None
        self._lock = threading.Lock()
        self._messages: dict[str, list[dict[str, Any]]] = {}
        self._metadata: dict[str, dict[str, Any]] = {}

    def initialize(self) -> None:
        pass

    def create(self, metadata: dict[str, Any] | None = None) -> str:
        conversation_id = str(uuid.uuid4())
        with self._lock:
            self._messages[conversation_id] = []
            self._metadata[conversation_id] = metadata or {}
        return conversation_id

    def metadata(self, conversation_id: str) -> dict[str, Any]:
        return dict(self._metadata.get(conversation_id, {}))

    def update_metadata(self, conversation_id: str, values: dict[str, Any]) -> None:
        with self._lock:
            self._metadata.setdefault(conversation_id, {}).update(values)

    def conversation_for_discord_thread(self, thread_id: str, active_days: int = 30) -> str | None:
        cutoff = datetime.now(UTC) - timedelta(days=active_days)
        for conversation_id, metadata in self._metadata.items():
            if metadata.get("discord_thread_id") != thread_id:
                continue
            messages = self._messages.get(conversation_id, [])
            last_at = messages[-1]["created_at"] if messages else metadata.get("created_at")
            if last_at and datetime.fromisoformat(str(last_at)) >= cutoff:
                return conversation_id
        return None

    def exists(self, conversation_id: str) -> bool:
        try:
            uuid.UUID(conversation_id)
        except ValueError:
            return False
        return conversation_id in self._messages

    def messages(self, conversation_id: str, limit: int = 40) -> list[dict[str, Any]]:
        return list(self._messages.get(conversation_id, []))[-limit:]

    def append(
        self,
        conversation_id: str,
        role: str,
        content: str,
        model: str | None = None,
        sources: list[dict[str, Any]] | None = None,
    ) -> None:
        item = {
            "role": role,
            "content": content,
            "model": model,
            "sources": sources or [],
            "created_at": datetime.now(UTC).isoformat(),
        }
        with self._lock:
            self._messages.setdefault(conversation_id, []).append(item)

    def list_conversations(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        items = [
            {
                "id": conversation_id,
                "message_count": len(messages),
                "preview": messages[0]["content"][:160],
                "updated_at": messages[-1]["created_at"],
            }
            for conversation_id, messages in reversed(list(self._messages.items()))
            if messages
        ]
        return items[offset : offset + limit]
