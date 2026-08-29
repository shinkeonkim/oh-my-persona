from oh_my_persona.agent import (
    MAX_SOURCE_CONTEXT_CHARS,
    MAX_TOTAL_CONTEXT_CHARS,
    build_context,
)


def test_context_is_bounded_for_minified_sources() -> None:
    hits = [
        {"text": "z" * 800_000, "url": f"https://example.com/{index}", "observed_at": None}
        for index in range(10)
    ]
    context = build_context(hits)
    assert context.count("<source ") == MAX_TOTAL_CONTEXT_CHARS // MAX_SOURCE_CONTEXT_CHARS
    assert context.count("z") == MAX_TOTAL_CONTEXT_CHARS
