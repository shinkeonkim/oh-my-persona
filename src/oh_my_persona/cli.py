from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audit import write_audit
from .collect import collect_local_repository
from .corpus import build_chunks, iter_corpus_files, read_jsonl, validate
from .ingest import approve_inbox, inspect_inbox
from .qa import build_answers
from .service import search
from .web_collect import collect_web_source


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(prog="persona")
    parser.add_argument("command", choices=("validate", "inventory", "chunk", "audit", "collect-local", "collect-web", "inspect-inbox", "ingest-inbox", "build-answers", "evaluate"))
    parser.add_argument("--approve", action="store_true", help="required before copying inbox files to raw")
    parser.add_argument("--source-id")
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--answers", type=Path)
    args = parser.parse_args()
    root = project_root()

    if args.command == "validate":
        errors = validate(root)
        if errors:
            raise SystemExit("\n".join(errors))
        print("corpus metadata is valid")
    elif args.command == "inventory":
        sources = read_jsonl(root / "data/registry/sources.jsonl")
        claims = read_jsonl(root / "data/curated/claims.jsonl")
        documents = read_jsonl(root / "data/registry/documents.jsonl")
        chunks = build_chunks(root)
        print(json.dumps({"sources": len(sources), "claims": len(claims), "documents": len(documents), "authored_documents": len(list(iter_corpus_files(root))), "chunks": len(chunks)}, ensure_ascii=False))
    elif args.command == "chunk":
        output = root / "data/processed/chunks.jsonl"
        output.parent.mkdir(parents=True, exist_ok=True)
        chunks = build_chunks(root)
        output.write_text("".join(json.dumps(chunk, ensure_ascii=False) + "\n" for chunk in chunks), encoding="utf-8")
        print(f"wrote {len(chunks)} chunks to {output.relative_to(root)}")
    elif args.command == "audit":
        report = write_audit(root)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if not report["quality_gate_500"]:
            raise SystemExit(1)
    elif args.command == "collect-local":
        if not args.source_id or not args.repo:
            raise SystemExit("collect-local requires --source-id and --repo")
        sources = read_jsonl(root / "data/registry/sources.jsonl")
        source = next((item for item in sources if item["source_id"] == args.source_id), None)
        if not source or source.get("source_type") != "repository":
            raise SystemExit("source-id must identify a registered repository")
        print(json.dumps(collect_local_repository(root, args.repo, source), ensure_ascii=False))
    elif args.command == "collect-web":
        if not args.source_id:
            raise SystemExit("collect-web requires --source-id")
        sources = read_jsonl(root / "data/registry/sources.jsonl")
        source = next((item for item in sources if item["source_id"] == args.source_id), None)
        if not source or source.get("collection") != "web":
            raise SystemExit("source-id must identify a registered web source")
        print(json.dumps(collect_web_source(root, source), ensure_ascii=False))
    elif args.command in {"inspect-inbox", "ingest-inbox"}:
        if args.command == "ingest-inbox" and not args.approve:
            raise SystemExit("ingest-inbox requires --approve")
        findings = approve_inbox(root) if args.command == "ingest-inbox" else inspect_inbox(root)
        print(json.dumps([finding.__dict__ for finding in findings], ensure_ascii=False, indent=2))
        if any(finding.status == "rejected" for finding in findings):
            raise SystemExit(2)
    elif args.command == "build-answers":
        if not args.answers:
            raise SystemExit("build-answers requires --answers")
        print(json.dumps(build_answers(root, args.answers), ensure_ascii=False))
    else:
        evaluations = read_jsonl(root / "evals/questions.jsonl")
        failures = []
        for evaluation in evaluations:
            hits = search(evaluation["question"], 10)
            source_ids = {hit.get("source_id") for hit in hits}
            expected = set(evaluation["required_source_ids"])
            if expected and not expected.intersection(source_ids):
                failures.append({"id": evaluation["id"], "expected_any_source": sorted(expected)})
        print(json.dumps({"evaluations": len(evaluations), "failures": failures}, ensure_ascii=False))
        if failures:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
