from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import shutil
import zipfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

from .models import InboxFinding

ALLOWED_SUFFIXES = {".md", ".markdown", ".txt", ".pdf", ".html", ".htm", ".json"}
EXECUTABLE_SUFFIXES = {".exe", ".dll", ".so", ".dylib", ".sh", ".bat", ".cmd", ".ps1"}
MAX_FILE_BYTES = 50 * 1024 * 1024
MAX_ARCHIVE_BYTES = 500 * 1024 * 1024
MAX_ARCHIVE_FILES = 10_000
SENSITIVE_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "korean_rrn": re.compile(r"\b\d{6}-[1-4]\d{6}\b"),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_file(path: Path) -> InboxFinding:
    reasons: list[str] = []
    suffix = path.suffix.lower()
    if path.is_symlink():
        reasons.append("symlink is not accepted")
    if path.stat().st_size > MAX_FILE_BYTES:
        reasons.append("file exceeds 50 MiB")
    if suffix in EXECUTABLE_SUFFIXES or suffix not in ALLOWED_SUFFIXES | {".zip"}:
        reasons.append("unsupported or executable file type")
    if suffix in ALLOWED_SUFFIXES - {".pdf"} and path.stat().st_size <= MAX_FILE_BYTES:
        sample = path.read_bytes()[:2_000_000].decode("utf-8", errors="ignore")
        reasons.extend(
            f"sensitive pattern: {name}"
            for name, pattern in SENSITIVE_PATTERNS.items()
            if pattern.search(sample)
        )
    if suffix == ".zip":
        reasons.extend(inspect_zip(path))
    status = "rejected" if reasons else "accepted"
    return InboxFinding(
        str(path),
        status,
        sha256_file(path),
        mimetypes.guess_type(path.name)[0] or "application/octet-stream",
        tuple(reasons),
    )


def inspect_zip(path: Path) -> list[str]:
    reasons: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            members = archive.infolist()
            if len(members) > MAX_ARCHIVE_FILES:
                reasons.append("archive contains more than 10,000 files")
            total = sum(member.file_size for member in members)
            if total > MAX_ARCHIVE_BYTES:
                reasons.append("expanded archive exceeds 500 MiB")
            for member in members:
                normalized = PurePosixPath(member.filename)
                if normalized.is_absolute() or ".." in normalized.parts:
                    reasons.append(f"unsafe archive path: {member.filename}")
                    break
                suffix = normalized.suffix.lower()
                if suffix and suffix not in ALLOWED_SUFFIXES:
                    reasons.append(f"unsupported archive member: {member.filename}")
                    break
                if member.compress_size and member.file_size / member.compress_size > 100:
                    reasons.append(f"suspicious compression ratio: {member.filename}")
                    break
    except zipfile.BadZipFile:
        reasons.append("invalid zip archive")
    return reasons


def inspect_inbox(root: Path) -> list[InboxFinding]:
    inbox = root / "data/inbox"
    return [
        inspect_file(path)
        for path in sorted(inbox.iterdir())
        if path.is_file() and path.name != ".gitkeep"
    ]


def approve_inbox(root: Path) -> list[InboxFinding]:
    findings = inspect_inbox(root)
    raw = root / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    for finding in findings:
        if finding.status != "accepted":
            continue
        source = Path(finding.path)
        destination = raw / f"{finding.sha256[:12]}-{source.name}"
        shutil.copy2(source, destination)
        metadata = {
            "original_name": source.name,
            "stored_name": destination.name,
            "sha256": finding.sha256,
            "mime": finding.mime,
            "ingested_at": timestamp,
            "review_status": "pending_metadata",
        }
        destination.with_suffix(destination.suffix + ".meta.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return findings
