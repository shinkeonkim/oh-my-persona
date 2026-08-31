from pathlib import Path

from oh_my_persona.application.knowledge.corpus import canonicalize_url, validate

ROOT = Path(__file__).resolve().parents[4]


def test_registry_and_claims_are_valid() -> None:
    assert validate(ROOT) == []


def test_canonical_url_drops_fragment() -> None:
    assert (
        canonicalize_url("https://GitHub.com/shinkeonkim/#bio") == "https://github.com/shinkeonkim"
    )
