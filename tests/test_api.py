from fastapi.testclient import TestClient

from oh_my_persona import api
from oh_my_persona.api import app
from oh_my_persona.conversations import RateLimiter

client = TestClient(app)


def test_health_and_models() -> None:
    assert client.get("/healthz").json() == {"status": "ok"}
    assert "persona-chat" in client.get("/api/models").json()["models"]
    assert client.get("/").status_code == 200


def test_widget_sdk_is_revalidated_after_deployment() -> None:
    response = client.get("/sdk/persona-widget.js")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-cache, must-revalidate"


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


def test_admin_can_send_a_direct_owner_reply(monkeypatch) -> None:
    monkeypatch.setenv("PERSONA_ADMIN_TOKEN", "test-admin-token")
    conversation_id = client.post("/api/conversations").json()["conversation_id"]
    headers = {"authorization": "Bearer test-admin-token"}
    response = client.post(
        f"/api/admin/conversations/{conversation_id}/messages",
        headers=headers,
        json={"content": "제가 직접 확인하고 남긴 답변입니다."},
    )
    assert response.status_code == 201
    assert response.json()["role"] == "owner"
    messages = client.get(f"/api/conversations/{conversation_id}").json()["messages"]
    assert messages[-1]["content"] == "제가 직접 확인하고 남긴 답변입니다."


def test_admin_can_fill_a_knowledge_gap_as_draft_then_publish(monkeypatch) -> None:
    monkeypatch.setenv("PERSONA_ADMIN_TOKEN", "test-admin-token")
    headers = {"authorization": "Bearer test-admin-token"}
    gaps = client.get("/api/admin/knowledge-gaps", headers=headers)
    assert gaps.status_code == 200
    assert len(gaps.json()["questions"]) == 50
    payload = {
        "answer": "운영진 대표 경험을 돌아보며 직접 작성한 답변입니다.",
        "answered_at": "2026-08-31",
        "visibility": "private",
        "evidence_urls": ["https://github.com/shinkeonkim"],
    }
    draft = client.post("/api/admin/knowledge-gaps/PQ-014/answer", headers=headers, json=payload)
    assert draft.status_code == 200
    assert draft.json()["status"] == "draft"
    assert client.get("/api/admin/knowledge-gaps", headers=headers).json()["summary"]["draft_answer"] >= 1
    payload["visibility"] = "public"
    published = client.post("/api/admin/knowledge-gaps/PQ-014/answer", headers=headers, json=payload)
    assert published.json()["status"] == "active"
    assert any(hit["chunk_id"].startswith("ADMIN-") for hit in client.get(
        "/api/search", params={"q": "운영진 대표 경험 직접 작성"}
    ).json()["hits"])


def test_docker_image_includes_knowledge_gap_report() -> None:
    dockerignore = (api.ROOT / ".dockerignore").read_text(encoding="utf-8")
    assert "!data/processed/knowledge-gaps.json" in dockerignore
