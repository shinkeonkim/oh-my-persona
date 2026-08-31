from pathlib import Path


def test_nullable_conversation_parameters_have_an_explicit_uuid_type() -> None:
    source = (
        Path(__file__).resolve().parents[3]
        / "oh_my_persona/infrastructure/persistence/abuse/postgres.py"
    ).read_text(encoding="utf-8")
    assert "%s::uuid IS NOT NULL" in source
    assert "conversation_id=%s::uuid" in source
