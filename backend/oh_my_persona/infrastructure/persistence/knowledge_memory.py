from __future__ import annotations

import builtins
import threading
import uuid
from datetime import UTC, datetime
from typing import Any


class MemoryKnowledgeStore:
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def initialize(self) -> None:
        pass

    def list(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        return list(self._items.values())[offset : offset + limit]

    def active(self) -> builtins.list[dict[str, Any]]:
        return [item for item in self.list(limit=5000) if item["status"] == "active"]

    def get(self, item_id: str) -> dict[str, Any] | None:
        return self._items.get(item_id) if _valid_uuid(item_id) else None

    def create(self, values: dict[str, Any]) -> dict[str, Any]:
        item_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()
        item = {"id": item_id, **values, "created_at": now, "updated_at": now}
        with self._lock:
            self._items[item_id] = item
        return item

    def update(self, item_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        with self._lock:
            current = self._items.get(item_id)
            if current is None:
                return None
            current.update(values)
            current["updated_at"] = datetime.now(UTC).isoformat()
            return dict(current)

    def delete(self, item_id: str) -> bool:
        with self._lock:
            return self._items.pop(item_id, None) is not None


class MemoryKnowledgeQuestionStore:
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def initialize(self) -> None:
        pass

    def list(self) -> list[dict[str, Any]]:
        return list(self._items.values())

    def get(self, question_id: str) -> dict[str, Any] | None:
        return (
            self._items.get(question_id) if _valid_uuid(question_id.removeprefix("AQ-")) else None
        )

    def create(self, values: dict[str, Any]) -> dict[str, Any]:
        question_id = f"AQ-{uuid.uuid4()}"
        item = {"question_id": question_id, **values, "created_at": datetime.now(UTC).isoformat()}
        with self._lock:
            self._items[question_id] = item
        return item

    def delete(self, question_id: str) -> bool:
        if not _valid_uuid(question_id.removeprefix("AQ-")):
            return False
        with self._lock:
            return self._items.pop(question_id, None) is not None


def _valid_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
    except ValueError:
        return False
    return True
