from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum


class BlockDuration(StrEnum):
    DAY = "24h"
    WEEK = "7d"
    PERMANENT = "permanent"

    def expires_at(self, now: datetime | None = None) -> datetime | None:
        current = now or datetime.now(UTC)
        if self is BlockDuration.DAY:
            return current + timedelta(days=1)
        if self is BlockDuration.WEEK:
            return current + timedelta(days=7)
        return None


@dataclass(frozen=True, slots=True)
class AbuseBlock:
    id: str
    identity_hash: str | None
    conversation_id: str | None
    reason: str
    note: str
    blocked_until: datetime | None
    created_by: str
    created_at: datetime
    revoked_at: datetime | None = None

    @property
    def active(self) -> bool:
        now = datetime.now(UTC)
        return self.revoked_at is None and (
            self.blocked_until is None or self.blocked_until > now
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "identity_hash": self.identity_hash,
            "identity_fingerprint": self.identity_hash[:12] if self.identity_hash else None,
            "conversation_id": self.conversation_id,
            "reason": self.reason,
            "note": self.note,
            "blocked_until": self.blocked_until.isoformat() if self.blocked_until else None,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "active": self.active,
        }
