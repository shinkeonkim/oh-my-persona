from oh_my_persona.infrastructure.llm.strands_agent import (
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


def test_meta_assistant_offer_on_a_new_line_is_removed() -> None:
    answer = (
        "제가 공개한 자료에서 확인됩니다.[3]\n\n원하면 면접용 30초 버전으로 다듬어드리겠습니다."
    )
    assert sanitize_persona_response(answer) == "제가 공개한 자료에서 확인됩니다.[3]"


def test_evidence_auditor_disclaimer_is_removed() -> None:
    answer = (
        "제가 공개한 자료에서는 미핏 프로젝트라는 이름을 직접적으로 확인하기는 어렵습니다. "
        "다만 제가 공개한 포트폴리오 자료에서 미핏 관련으로 보이는 기여는 확인됩니다. [4]\n\n"
        "미핏에서는 서버 API와 인프라를 개발했습니다. [5]"
    )
    assert sanitize_persona_response(answer) == "미핏에서는 서버 API와 인프라를 개발했습니다. [5]"


def test_evidence_frame_prefix_is_removed_but_experience_remains() -> None:
    answer = "제가 공개한 자료 기준으로는, 미핏에서 다음과 같은 일을 했습니다. [4]"
    assert sanitize_persona_response(answer) == "미핏에서 다음과 같은 일을 했습니다. [4]"


def test_trailing_role_disclaimer_is_removed() -> None:
    answer = (
        "미핏에서는 백엔드 개발을 맡았습니다. [3]\n\n"
        "다만 이것은 제가 공개한 자료에 남아 있는 기록을 바탕으로 한 것이고, 미핏에서의 역할을 "
        "하나로 딱 잘라 공식적으로 정리한 자료는 제가 공개한 자료에서는 확인하기 어렵습니다. [4]"
    )
    assert sanitize_persona_response(answer) == "미핏에서는 백엔드 개발을 맡았습니다. [3]"
