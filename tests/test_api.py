from fastapi.testclient import TestClient

from oh_my_persona import api
from oh_my_persona.api import app
from oh_my_persona.conversations import RateLimiter

client = TestClient(app)


def test_health_and_models() -> None:
    assert client.get("/healthz").json() == {"status": "ok"}
    assert "persona-chat" in client.get("/api/models").json()["models"]
    assert client.get("/").status_code == 200


def test_search_and_grounded_chat_without_credentials(monkeypatch) -> None:
    monkeypatch.delenv("PERSONA_LITELLM_URL", raising=False)
    monkeypatch.delenv("PERSONA_LITELLM_KEY", raising=False)
    assert client.get("/api/search", params={"q": "특전사"}).json()["hits"]
    response = client.post("/api/chat", json={"message": "특전사에서 언제 복무했나요?"})
    assert response.status_code == 200
    assert response.json()["sources"]


def test_source_not_found() -> None:
    assert client.get("/api/sources/SRC-9999").status_code == 404


def test_private_query_abstains() -> None:
    response = client.post("/api/chat", json={"message": "김신건의 주민등록번호는?"})
    assert response.status_code == 200
    assert response.json()["sources"] == []
    assert "개인정보" in response.json()["answer"]


def test_multiturn_conversation_is_saved(monkeypatch) -> None:
    monkeypatch.delenv("PERSONA_LITELLM_URL", raising=False)
    first = client.post(
        "/api/chat",
        headers={"cf-connecting-ip": "192.0.2.10"},
        json={"message": "특전사 복무 기간은?"},
    ).json()
    second = client.post(
        "/api/chat",
        headers={"cf-connecting-ip": "192.0.2.10"},
        json={"message": "그때 맡은 역할은?", "conversation_id": first["conversation_id"]},
    )
    assert second.status_code == 200
    saved = client.get(f"/api/conversations/{first['conversation_id']}").json()["messages"]
    assert [item["role"] for item in saved] == ["user", "assistant", "user", "assistant"]


def test_unknown_conversation_and_rate_limit(monkeypatch) -> None:
    missing = "00000000-0000-4000-8000-000000000000"
    assert client.get(f"/api/conversations/{missing}").status_code == 404
    monkeypatch.setattr(api, "limiter", RateLimiter(api.store, limit=1, window_seconds=60))
    headers = {"cf-connecting-ip": "192.0.2.99"}
    assert client.post("/api/chat", headers=headers, json={"message": "주민등록번호는?"}).status_code == 200
    limited = client.post("/api/chat", headers=headers, json={"message": "집 주소는?"})
    assert limited.status_code == 429
    assert int(limited.headers["retry-after"]) >= 1


def test_admin_auth_knowledge_crud_and_conversation_list(monkeypatch) -> None:
    monkeypatch.setenv("PERSONA_ADMIN_TOKEN", "test-admin-token")
    assert client.get("/api/admin/knowledge").status_code == 401
    headers = {"authorization": "Bearer test-admin-token"}
    payload = {
        "title": "관리자 인터뷰 기록",
        "content": "저는 관리자 입력 지식을 검색에 반영합니다.",
        "source_url": "https://shinkeonkim.com/admin-interview",
        "observed_at": "2026-08-30",
        "status": "active",
    }
    created = client.post("/api/admin/knowledge", headers=headers, json=payload)
    assert created.status_code == 201
    item_id = created.json()["id"]
    assert any(hit["chunk_id"] == f"ADMIN-{item_id}" for hit in client.get(
        "/api/search", params={"q": "관리자 입력 지식"}
    ).json()["hits"])
    payload["title"] = "수정된 기록"
    assert client.put(f"/api/admin/knowledge/{item_id}", headers=headers, json=payload).status_code == 200
    assert client.get("/api/admin/conversations", headers=headers).status_code == 200
    assert client.delete(f"/api/admin/knowledge/{item_id}", headers=headers).status_code == 204
