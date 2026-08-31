from __future__ import annotations

import threading
from dataclasses import replace
from datetime import UTC, datetime

from ....domain.abuse import AbuseBlock


class MemoryAbuseStore:
    def __init__(self) -> None:
        self._items: dict[str, AbuseBlock] = {}
        self._lock = threading.Lock()

    def initialize(self) -> None:
        pass

    def create(self, block: AbuseBlock) -> AbuseBlock:
        with self._lock:
            self._items[block.id] = block
        return block

    def active_for(self, identity_hash: str, conversation_id: str | None) -> AbuseBlock | None:
        for block in reversed(list(self._items.values())):
            if not block.active:
                continue
            if conversation_id and block.conversation_id == conversation_id:
                return block
            if identity_hash and block.identity_hash == identity_hash:
                return block
        return None

    def list(self, include_revoked: bool = True) -> list[AbuseBlock]:
        items = reversed(list(self._items.values()))
        return list(items) if include_revoked else [item for item in items if item.active]

    def revoke(self, block_id: str) -> AbuseBlock | None:
        with self._lock:
            item = self._items.get(block_id)
            if item is None:
                return None
            revoked = replace(item, revoked_at=datetime.now(UTC))
            self._items[block_id] = revoked
            return revoked
