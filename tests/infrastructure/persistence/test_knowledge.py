from oh_my_persona.infrastructure.persistence.knowledge import (
    KnowledgeQuestionStore,
    KnowledgeStore,
)
from oh_my_persona.infrastructure.persistence.knowledge_memory import (
    MemoryKnowledgeQuestionStore,
    MemoryKnowledgeStore,
)
from oh_my_persona.infrastructure.persistence.knowledge_postgres import (
    PostgresKnowledgeQuestionStore,
    PostgresKnowledgeStore,
)


def test_factory_selects_memory_adapters_without_database_url() -> None:
    assert isinstance(KnowledgeStore(), MemoryKnowledgeStore)
    assert isinstance(KnowledgeQuestionStore(), MemoryKnowledgeQuestionStore)


def test_factory_selects_postgres_adapters_with_database_url() -> None:
    url = "postgresql://persona:secret@database/persona"
    assert isinstance(KnowledgeStore(url), PostgresKnowledgeStore)
    assert isinstance(KnowledgeQuestionStore(url), PostgresKnowledgeQuestionStore)


def test_memory_knowledge_crud_and_active_filter() -> None:
    store = MemoryKnowledgeStore()
    active = store.create(_knowledge_values("active"))
    draft = store.create(_knowledge_values("draft"))

    assert [item["id"] for item in store.active()] == [active["id"]]
    updated = store.update(draft["id"], _knowledge_values("active"))
    assert updated is not None and updated["status"] == "active"
    assert store.delete(active["id"])
    assert store.get(active["id"]) is None


def test_memory_question_crud() -> None:
    store = MemoryKnowledgeQuestionStore()
    created = store.create(
        {"question": "무엇을 배웠나요?", "category": "reflection", "time_scope": "2026-08"}
    )

    assert store.get(created["question_id"]) == created
    assert store.list() == [created]
    assert store.delete(created["question_id"])
    assert store.list() == []


def _knowledge_values(status: str) -> dict[str, str]:
    return {
        "title": "직접 기록",
        "content": "제가 직접 작성한 지식입니다.",
        "source_url": "https://shinkeonkim.com/knowledge",
        "observed_at": "2026-08-31",
        "status": status,
    }
