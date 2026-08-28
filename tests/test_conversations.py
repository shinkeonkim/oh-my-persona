from oh_my_persona.conversations import ConversationStore, RateLimiter


def test_memory_store_and_rate_limit() -> None:
    store = ConversationStore(database_url=None)
    conversation_id = store.create()
    store.append(conversation_id, "user", "첫 질문")
    store.append(conversation_id, "assistant", "첫 답변", sources=[{"source_id": "SRC-1"}])
    assert store.exists(conversation_id)
    assert [item["role"] for item in store.messages(conversation_id)] == ["user", "assistant"]

    limiter = RateLimiter(store, limit=2, window_seconds=60)
    assert limiter.consume("visitor")[0]
    assert limiter.consume("visitor")[0]
    allowed, retry_after = limiter.consume("visitor")
    assert not allowed
    assert retry_after > 0
