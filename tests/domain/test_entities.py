from oh_my_persona.domain import ConversationMessage, SourceReference


def test_domain_message_is_immutable_and_typed() -> None:
    source = SourceReference(source_id="SRC-1", url="https://example.com")
    message = ConversationMessage(role="assistant", content="답변입니다.", sources=(source,))

    assert message.sources[0].source_id == "SRC-1"
