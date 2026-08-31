from oh_my_persona.infrastructure.github import select_document_paths


def test_document_paths_prioritize_docs_and_exclude_readme() -> None:
    tree = [
        {"type": "blob", "path": "README.md"},
        {"type": "blob", "path": "docs/architecture.md"},
        {"type": "blob", "path": ".github/CONTRIBUTING.md"},
        {"type": "blob", "path": "src/notes.md"},
        {"type": "blob", "path": "DESIGN.md"},
        {"type": "tree", "path": "docs"},
    ]
    assert select_document_paths(tree) == [
        ".github/CONTRIBUTING.md",
        "docs/architecture.md",
        "DESIGN.md",
    ]
