from fastapi.testclient import TestClient

from oh_my_persona.api import app

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
