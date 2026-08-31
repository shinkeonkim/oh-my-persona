import zipfile
from pathlib import Path

from oh_my_persona.infrastructure.collection.inbox import inspect_file


def test_rejects_zip_path_traversal(tmp_path: Path) -> None:
    archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("../escape.md", "unsafe")
    finding = inspect_file(archive)
    assert finding.status == "rejected"
    assert any("unsafe archive path" in reason for reason in finding.reasons)


def test_rejects_sensitive_material(tmp_path: Path) -> None:
    document = tmp_path / "secret.md"
    document.write_text("-----BEGIN PRIVATE KEY-----\nsecret", encoding="utf-8")
    assert inspect_file(document).status == "rejected"
