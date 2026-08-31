import ast
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[2] / "src" / "oh_my_persona"


def test_production_python_modules_stay_below_300_lines() -> None:
    source_root = PACKAGE_ROOT
    oversized = {
        str(path.relative_to(source_root)): len(path.read_text(encoding="utf-8").splitlines())
        for path in source_root.rglob("*.py")
        if len(path.read_text(encoding="utf-8").splitlines()) > 300
    }
    assert oversized == {}, f"Split modules by responsibility: {oversized}"


def test_github_collection_package_exports_public_commands() -> None:
    from oh_my_persona.infrastructure import github

    assert callable(github.collect_deep)
    assert callable(github.collect_pull_requests)
    assert callable(github.collect_public_docs)
    assert callable(github.collect_priority_trees)


def test_root_contains_only_package_initializer() -> None:
    root_modules = sorted(path.name for path in PACKAGE_ROOT.glob("*.py"))
    assert root_modules == ["__init__.py"]


def test_inner_layers_do_not_depend_on_outer_layers() -> None:
    forbidden = {
        "domain": (
            "oh_my_persona.application",
            "oh_my_persona.infrastructure",
            "oh_my_persona.presentation",
        ),
        "infrastructure": ("oh_my_persona.application", "oh_my_persona.presentation"),
        "application": ("oh_my_persona.infrastructure", "oh_my_persona.presentation"),
    }
    violations: list[str] = []
    for layer, prefixes in forbidden.items():
        for path in (PACKAGE_ROOT / layer).rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    resolved = _resolve_import(path, node)
                    if resolved.startswith(prefixes):
                        violations.append(f"{path.relative_to(PACKAGE_ROOT)} -> {resolved}")
    assert violations == []


def _resolve_import(path: Path, node: ast.ImportFrom) -> str:
    if node.level == 0:
        return node.module or ""
    package_parts = list(path.relative_to(PACKAGE_ROOT).with_suffix("").parts[:-1])
    keep = max(0, len(package_parts) - node.level + 1)
    suffix = (node.module or "").split(".") if node.module else []
    return ".".join(("oh_my_persona", *package_parts[:keep], *suffix))
