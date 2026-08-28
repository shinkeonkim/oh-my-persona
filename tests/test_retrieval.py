from pathlib import Path

from oh_my_persona.retrieval import MemoryRetriever

ROOT = Path(__file__).resolve().parents[1]


def test_temporal_military_search_has_public_citation() -> None:
    hits = MemoryRetriever(ROOT).search("군 복무 특전사 2022 2024", 5)
    assert hits
    assert any(hit.source_id == "SRC-0001" for hit in hits)
    assert all(hit.url.startswith("https://") for hit in hits if hit.source_id)


def test_unknown_subject_returns_no_claim() -> None:
    hits = MemoryRetriever(ROOT).search("주민등록번호", 5)
    assert all(hit.metadata.get("claim_id") is None for hit in hits)
