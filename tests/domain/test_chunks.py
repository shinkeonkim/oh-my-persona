from oh_my_persona.domain.chunks import chunk_text


def test_chunk_ids_are_stable_and_content_is_preserved() -> None:
    first = chunk_text("첫 문단\n\n둘째 문단", "sample.md", max_chars=6)
    second = chunk_text("첫 문단\n\n둘째 문단", "sample.md", max_chars=6)
    assert first == second
    assert [chunk.text for chunk in first] == ["첫 문단", "둘째 문단"]
