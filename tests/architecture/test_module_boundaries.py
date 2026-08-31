from pathlib import Path


def test_production_python_modules_stay_below_300_lines() -> None:
    source_root = Path(__file__).parents[2] / "src" / "oh_my_persona"
    oversized = {
        str(path.relative_to(source_root)): len(path.read_text(encoding="utf-8").splitlines())
        for path in source_root.rglob("*.py")
        if len(path.read_text(encoding="utf-8").splitlines()) > 300
    }
    assert oversized == {}, f"Split modules by responsibility: {oversized}"


def test_github_collection_facade_keeps_public_commands() -> None:
    from oh_my_persona import github_deep

    assert callable(github_deep.collect_deep)
    assert callable(github_deep.collect_pull_requests)
    assert callable(github_deep.collect_public_docs)
    assert callable(github_deep.collect_priority_trees)
