from __future__ import annotations

import pytest

from oh_my_persona.application.abuse import AbuseService, BlockedIdentityError
from oh_my_persona.domain.abuse import BlockDuration
from oh_my_persona.infrastructure.persistence.abuse import AbuseStore
from oh_my_persona.infrastructure.persistence.conversations import ConversationStore


def test_conversation_and_identity_blocks_are_independent() -> None:
    conversations = ConversationStore()
    repository = AbuseStore()
    service = AbuseService(repository, conversations)
    identity = service.identity_hash("192.0.2.30")
    conversation_id = conversations.create({"identity_hash": identity})

    conversation_block = service.block_conversation(
        conversation_id, BlockDuration.DAY, "대화 악용", "감사 기록"
    )
    with pytest.raises(BlockedIdentityError):
        service.guard("different-identity", conversation_id)
    service.revoke(conversation_block.id)
    service.guard("different-identity", conversation_id)

    identity_block = service.block_identity_for_conversation(
        conversation_id, BlockDuration.WEEK, "반복적인 자동 요청", ""
    )
    with pytest.raises(BlockedIdentityError):
        service.guard(identity, None)
    assert identity_block.as_dict()["identity_fingerprint"] == identity[:12]


def test_identity_block_requires_a_bound_conversation() -> None:
    conversations = ConversationStore()
    service = AbuseService(AbuseStore(), conversations)
    conversation_id = conversations.create()
    with pytest.raises(ValueError, match="식별 정보"):
        service.block_identity_for_conversation(
            conversation_id, BlockDuration.PERMANENT, "악성 사용자", ""
        )
