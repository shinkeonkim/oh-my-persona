from pathlib import Path

from oh_my_persona.infrastructure.retrieval import MemoryRetriever

ROOT = Path(__file__).resolve().parents[4]


def test_temporal_military_search_has_public_citation() -> None:
    hits = MemoryRetriever(ROOT).search("군 복무 특전사 2022 2024", 5)
    assert hits
    assert any(hit.source_id == "SRC-0001" for hit in hits)
    assert all(hit.url.startswith("https://") for hit in hits if hit.source_id)


def test_unknown_subject_returns_no_claim() -> None:
    hits = MemoryRetriever(ROOT).search("주민등록번호", 5)
    assert all(hit.metadata.get("claim_id") is None for hit in hits)


def test_mefit_alias_prioritizes_capstone_repositories() -> None:
    hits = MemoryRetriever(ROOT).search("미핏 프로젝트에서 어떤 일을 했나요?", 8)
    source_ids = [hit.source_id for hit in hits[:4]]
    assert "SRC-0072" in source_ids or "SRC-0076" in source_ids
