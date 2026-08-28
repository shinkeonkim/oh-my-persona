from pathlib import Path

from oh_my_persona.corpus import canonicalize_url, chunk_text, validate

ROOT = Path(__file__).resolve().parents[1]


def test_registry_and_claims_are_valid() -> None:
    assert validate(ROOT) == []


def test_chunk_ids_are_stable_and_content_is_preserved() -> None:
    first = chunk_text("첫 문단\n\n둘째 문단", "sample.md", max_chars=6)
    second = chunk_text("첫 문단\n\n둘째 문단", "sample.md", max_chars=6)
    assert first == second
    assert [chunk.text for chunk in first] == ["첫 문단", "둘째 문단"]


def test_canonical_url_drops_fragment() -> None:
    assert canonicalize_url("https://GitHub.com/shinkeonkim/#bio") == "https://github.com/shinkeonkim"
