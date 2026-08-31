from oh_my_persona.application import ChatUseCase
from oh_my_persona.conversations import ConversationStore


def test_chat_use_case_creates_and_persists_exchange() -> None:
    store = ConversationStore()
    use_case = ChatUseCase(store, lambda question, model, history: (f"답변: {question}", []))

    result = use_case.execute("질문", None, None)

    assert result.answer == "답변: 질문"
    assert [message["role"] for message in store.messages(result.conversation_id)] == [
        "user",
        "assistant",
    ]


def test_chat_use_case_rejects_unknown_conversation() -> None:
    store = ConversationStore()
    use_case = ChatUseCase(store, lambda question, model, history: ("답변", []))

    try:
        use_case.execute("질문", None, "missing")
    except LookupError as error:
        assert str(error) == "conversation not found"
    else:
        raise AssertionError("LookupError was not raised")
