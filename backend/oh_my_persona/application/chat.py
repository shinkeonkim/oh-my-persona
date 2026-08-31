from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..domain.repositories import ConversationRepository

Record = dict[str, Any]
AnswerFunction = Callable[[str, str | None, list[Record] | None], tuple[str, list[Record]]]


@dataclass(frozen=True, slots=True)
class ChatResult:
    conversation_id: str
    answer: str
    sources: list[Record]


class ChatUseCase:
    """Coordinates one synchronous exchange without knowing HTTP or PostgreSQL."""

    def __init__(self, conversations: ConversationRepository, answer_question: AnswerFunction):
        self._conversations = conversations
        self._answer_question = answer_question

    def execute(self, message: str, model: str | None, conversation_id: str | None) -> ChatResult:
        current_id = conversation_id or self._conversations.create()
        if not self._conversations.exists(current_id):
            raise LookupError("conversation not found")
        history = self._conversations.messages(current_id, 20)
        response, sources = self._answer_question(message, model, history)
        self._conversations.append(current_id, "user", message)
        self._conversations.append(current_id, "assistant", response, model, sources)
        return ChatResult(current_id, response, sources)
