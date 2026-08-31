from __future__ import annotations

import hashlib
import os
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from ...domain.abuse import AbuseBlock, AbuseRepository, BlockDuration
from ...domain.repositories import ConversationRepository


class BlockedIdentityError(PermissionError):
    def __init__(self, block: AbuseBlock):
        super().__init__("관리자에 의해 대화 이용이 제한되었습니다.")
        self.block = block


@dataclass(frozen=True, slots=True)
class AbuseService:
    repository: AbuseRepository
    conversations: ConversationRepository

    def identity_hash(self, client_ip: str) -> str:
        salt = os.environ.get("PERSONA_RATE_LIMIT_SALT", "persona-public")
        return hashlib.sha256(f"{salt}:{client_ip}".encode()).hexdigest()

    def guard(self, identity_hash: str, conversation_id: str | None = None) -> None:
        block = self.repository.active_for(identity_hash, conversation_id)
        if block:
            raise BlockedIdentityError(block)

    def bind(self, conversation_id: str, identity_hash: str) -> None:
        self.conversations.update_metadata(conversation_id, {"identity_hash": identity_hash})

    def block_conversation(
        self, conversation_id: str, duration: BlockDuration, reason: str, note: str
    ) -> AbuseBlock:
        if not self.conversations.exists(conversation_id):
            raise LookupError("conversation not found")
        block = AbuseBlock(
            id=str(uuid.uuid4()), identity_hash=None, conversation_id=conversation_id,
            reason=reason, note=note, blocked_until=duration.expires_at(),
            created_by="admin", created_at=datetime.now(UTC),
        )
        return self.repository.create(block)

    def block_identity_for_conversation(
        self, conversation_id: str, duration: BlockDuration, reason: str, note: str
    ) -> AbuseBlock:
        if not self.conversations.exists(conversation_id):
            raise LookupError("conversation not found")
        identity_hash = self.conversations.metadata(conversation_id).get("identity_hash")
        if not identity_hash:
            raise ValueError("이 대화에는 차단 가능한 사용자 식별 정보가 없습니다.")
        block = AbuseBlock(
            id=str(uuid.uuid4()), identity_hash=str(identity_hash),
            conversation_id=conversation_id, reason=reason, note=note,
            blocked_until=duration.expires_at(), created_by="admin",
            created_at=datetime.now(UTC),
        )
        return self.repository.create(block)

    def status(self, conversation_id: str) -> dict[str, object]:
        metadata = self.conversations.metadata(conversation_id)
        identity_hash = str(metadata.get("identity_hash", ""))
        block = self.repository.active_for(identity_hash, conversation_id)
        return {
            "blocked": block is not None,
            "identity_fingerprint": identity_hash[:12] or None,
            "block": block.as_dict() if block else None,
        }

    def list_blocks(self) -> list[dict[str, object]]:
        return [item.as_dict() for item in self.repository.list()]

    def revoke(self, block_id: str) -> AbuseBlock:
        block = self.repository.revoke(block_id)
        if block is None:
            raise LookupError("block not found")
        return block
