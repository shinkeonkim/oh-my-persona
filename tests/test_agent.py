from oh_my_persona.agent import (
    MAX_SOURCE_CONTEXT_CHARS,
    MAX_TOTAL_CONTEXT_CHARS,
    SYSTEM_PROMPT,
    build_context,
    sanitize_persona_response,
)


def test_context_is_bounded_for_minified_sources() -> None:
    hits = [
        {"text": "z" * 800_000, "url": f"https://example.com/{index}", "observed_at": None}
        for index in range(10)
    ]
    context = build_context(hits)
    assert context.count("<source ") == MAX_TOTAL_CONTEXT_CHARS // MAX_SOURCE_CONTEXT_CHARS
    assert context.count("z") == MAX_TOTAL_CONTEXT_CHARS


def test_persona_prompt_is_first_person_and_polite() -> None:
    assert "김신건 본인" in SYSTEM_PROMPT
    assert "1인칭" in SYSTEM_PROMPT
    assert "존댓말" in SYSTEM_PROMPT
    assert "글쓰기 도우미" in SYSTEM_PROMPT
    assert "원하시면" in SYSTEM_PROMPT


def test_meta_assistant_offer_is_removed() -> None:
    answer = "저는 API 안정성을 중요하게 생각합니다. 원하시면 면접 답변용 30초 버전으로 다듬어드리겠습니다."
    assert sanitize_persona_response(answer) == "저는 API 안정성을 중요하게 생각합니다."
