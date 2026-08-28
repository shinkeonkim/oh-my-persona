from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .corpus import read_jsonl
from .ingest import SENSITIVE_PATTERNS


def audit_corpus(root: Path) -> dict:
    chunks = read_jsonl(root / "data/processed/chunks.jsonl")
    documents = read_jsonl(root / "data/registry/documents.jsonl")
    hashes = Counter(item["content_sha256"] for item in chunks)
    exact_duplicates = sum(count - 1 for count in hashes.values() if count > 1)
    traceable = sum(bool(item.get("canonical_url") and item.get("document_id") and item.get("source_id")) for item in chunks)
    sensitive: list[dict[str, str]] = []
    for item in chunks:
        for name, pattern in SENSITIVE_PATTERNS.items():
            if pattern.search(item["text"]):
                sensitive.append({"chunk_id": item["chunk_id"], "pattern": name})
    per_source = Counter(item.get("source_id") or "authored" for item in chunks)
    return {
        "documents": len(documents), "chunks": len(chunks),
        "exact_duplicates": exact_duplicates,
        "traceable_chunks": traceable,
        "traceability_rate": round(traceable / len(chunks), 4) if chunks else 0,
        "sensitive_findings": sensitive,
        "chunks_per_source": dict(sorted(per_source.items())),
        "quality_gate_500": len(chunks) >= 500 and exact_duplicates == 0 and not sensitive,
    }


def write_audit(root: Path) -> dict:
    report = audit_corpus(root)
    destination = root / "data/processed/audit-report.json"
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
