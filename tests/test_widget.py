from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from oh_my_persona import api
from oh_my_persona.api import app
from oh_my_persona.conversations import ConversationStore
from oh_my_persona.discord_bridge import DiscordBridge
from oh_my_persona.sessions import create_widget_session

client = TestClient(app)


def test_widget_session_requires_its_access_token() -> None:
    created = client.post(
        "/api/widget/sessions",
        headers={"origin": "https://portfolio.shinkeonkim.com"},
    )
    assert created.status_code == 201
    session = created.json()
    url = f"/api/widget/conversations/{session['conversation_id']}"
    assert client.get(url).status_code == 422
    assert client.get(url, headers={"x-persona-session-token": "wrong-token-value-that-is-long"}).status_code == 401
    assert client.get(url, headers={"x-persona-session-token": session["token"]}).status_code == 200


def test_widget_chat_reuses_authorized_conversation(monkeypatch) -> None:
    monkeypatch.setattr(api, "answer", lambda *_: ("제가 직접 답하는 내용입니다.", []))
    session = client.post("/api/widget/sessions").json()
    response = client.post(
        "/api/widget/chat",
        json={**session, "message": "어떤 개발자인가요?"},
    )
    assert response.status_code == 200
    saved = client.get(
        f"/api/widget/conversations/{session['conversation_id']}",
        headers={"x-persona-session-token": session["token"]},
    ).json()["messages"]
    assert [item["role"] for item in saved] == ["user", "assistant"]


def test_discord_owner_reply_is_delivered_only_to_recent_linked_session(monkeypatch) -> None:
    monkeypatch.setenv("PERSONA_DISCORD_OWNER_IDS", "42")
    store = ConversationStore()
    recent_id, _ = create_widget_session(store)
    store.update_metadata(recent_id, {"discord_thread_id": "100"})
    bridge = DiscordBridge(store)
    assert bridge.accept_owner_message("100", "7", "허용되지 않은 사용자") is None
    assert bridge.accept_owner_message("100", "42", "제가 직접 남긴 답변입니다.") == recent_id
    assert store.messages(recent_id)[-1]["role"] == "owner"

    old_id, _ = create_widget_session(store)
    store.update_metadata(old_id, {
        "discord_thread_id": "200",
        "created_at": (datetime.now(UTC) - timedelta(days=31)).isoformat(),
    })
    assert bridge.accept_owner_message("200", "42", "늦은 답변") is None


def test_discord_owner_allowlist_is_required(monkeypatch) -> None:
    monkeypatch.delenv("PERSONA_DISCORD_OWNER_IDS", raising=False)
    store = ConversationStore()
    conversation_id, _ = create_widget_session(store)
    store.update_metadata(conversation_id, {"discord_thread_id": "300"})
    assert DiscordBridge(store).accept_owner_message("300", "42", "답변") is None


def test_widget_cors_allows_only_registered_sites() -> None:
    allowed = client.options(
        "/api/widget/sessions",
        headers={
            "origin": "https://portfolio.shinkeonkim.com",
            "access-control-request-method": "POST",
        },
    )
    assert allowed.headers["access-control-allow-origin"] == "https://portfolio.shinkeonkim.com"
    denied = client.options(
        "/api/widget/sessions",
        headers={
            "origin": "https://attacker.example",
            "access-control-request-method": "POST",
        },
    )
    assert "access-control-allow-origin" not in denied.headers
