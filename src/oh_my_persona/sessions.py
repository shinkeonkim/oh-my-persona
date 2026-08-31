from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import UTC, datetime

from .conversations import ConversationStore


def _secret() -> bytes:
    value = os.environ.get("PERSONA_SESSION_SECRET")
    if value:
        return value.encode()
    return b"persona-development-session-secret"


def token_hash(token: str) -> str:
    return hmac.new(_secret(), token.encode(), hashlib.sha256).hexdigest()


def create_widget_session(store: ConversationStore, origin: str | None = None) -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    conversation_id = store.create({
        "widget_token_hash": token_hash(token),
        "widget_origin": origin or "unknown",
        "created_at": datetime.now(UTC).isoformat(),
    })
    return conversation_id, token


def verify_widget_session(store: ConversationStore, conversation_id: str, token: str) -> bool:
    if not store.exists(conversation_id) or not token:
        return False
    expected = store.metadata(conversation_id).get("widget_token_hash", "")
    return bool(expected) and hmac.compare_digest(expected, token_hash(token))
