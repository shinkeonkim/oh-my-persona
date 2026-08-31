from datetime import date

from pydantic import AnyHttpUrl, BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    model: str | None = None
    conversation_id: str | None = None


class WidgetChatRequest(ChatRequest):
    conversation_id: str
    token: str = Field(min_length=20, max_length=200)


class KnowledgeRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=50_000)
    source_url: AnyHttpUrl
    observed_at: date | None = None
    status: str = Field(pattern="^(active|draft)$")


class AdminConversationMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class KnowledgeGapAnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=50_000)
    answered_at: date
    visibility: str = Field(pattern="^(private|public)$")
    evidence_urls: list[AnyHttpUrl] = Field(default_factory=list, max_length=20)


class KnowledgeGapQuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    category: str = Field(min_length=1, max_length=80)
    time_scope: str = Field(min_length=1, max_length=80)
