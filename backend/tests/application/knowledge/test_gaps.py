import json
from pathlib import Path
from shutil import copy

from oh_my_persona.application.knowledge.gaps import (
    analyze_knowledge_gaps,
    write_knowledge_gap_outputs,
)
from oh_my_persona.domain.search import SearchHit

ROOT = Path(__file__).resolve().parents[4]


class EmptyRetriever:
    def search(self, query: str, limit: int = 6) -> list[SearchHit]:
        return []


def test_gap_report_ranks_questions_and_writes_private_template(tmp_path: Path) -> None:
    project = tmp_path / "project"
    for directory in ("data/questionnaires", "data/registry", "data/curated", "data/processed"):
        (project / directory).mkdir(parents=True, exist_ok=True)
    copy(ROOT / "data/questionnaires/persona-questions.jsonl", project / "data/questionnaires")
    (project / "data/registry/sources.jsonl").write_text("", encoding="utf-8")
    (project / "data/curated/claims.jsonl").write_text("", encoding="utf-8")
    retriever = EmptyRetriever()
    report = analyze_knowledge_gaps(project, retriever)
    assert report["summary"] == {"empty": 50}
    output = project / "data/processed/gaps.json"
    template = project / "answers.jsonl"
    result = write_knowledge_gap_outputs(project, output, template, retriever)
    first = json.loads(template.read_text(encoding="utf-8").splitlines()[0])
    assert result["unanswered"] == 50
    assert first["visibility"] == "private"
    assert json.loads(output.read_text(encoding="utf-8"))["questions"][0]["priority"] == 3
