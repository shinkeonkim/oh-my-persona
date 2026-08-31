import json
from pathlib import Path
from shutil import copy

from oh_my_persona.application.knowledge.qa import build_answers

ROOT = Path(__file__).resolve().parents[4]


def test_build_answers_only_promotes_public_answers(tmp_path: Path) -> None:
    project = tmp_path / "project"
    (project / "data/questionnaires").mkdir(parents=True)
    (project / "data/registry").mkdir(parents=True)
    (project / "data/curated").mkdir(parents=True)
    copy(ROOT / "data/questionnaires/persona-questions.jsonl", project / "data/questionnaires")
    (project / "data/registry/documents.jsonl").write_text("", encoding="utf-8")
    answers = project / "answers.jsonl"
    rows = [
        {
            "question_id": "PQ-001",
            "answer": "공개 답변",
            "answered_at": "2026-08-29",
            "visibility": "public",
        },
        {
            "question_id": "PQ-002",
            "answer": "비공개 답변",
            "answered_at": "2026-08-29",
            "visibility": "private",
        },
    ]
    answers.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    assert build_answers(project, answers) == {"accepted": 1, "skipped": 1}
    assert "공개 답변" in (project / "data/curated/persona-interview-answers.md").read_text()
    assert "비공개 답변" not in (project / "data/curated/persona-interview-answers.md").read_text()
