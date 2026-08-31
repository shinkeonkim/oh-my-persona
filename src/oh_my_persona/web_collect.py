from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.robotparser
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx

from .ingest import SENSITIVE_PATTERNS

USER_AGENT = "oh-my-persona-research/0.1 (+https://github.com/shinkeonkim/oh-my-persona)"
MAX_RESPONSE_BYTES = 10 * 1024 * 1024


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.ignored = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "svg", "noscript"}:
            self.ignored += 1
        elif tag in {"p", "div", "section", "article", "h1", "h2", "h3", "h4", "li", "br", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "svg", "noscript"} and self.ignored:
            self.ignored -= 1

    def handle_data(self, data: str) -> None:
        if not self.ignored:
            self.parts.append(data)

    def text(self) -> str:
        joined = " ".join(part.strip() for part in self.parts if part.strip())
        return re.sub(r"\n\s*\n+", "\n\n", joined).strip()


def collect_web_source(
    root: Path, source: dict[str, Any], delay_seconds: float = 1.0
) -> dict[str, Any]:
    url = source["canonical_url"]
    _assert_robots_allowed(url)
    time.sleep(max(0.0, delay_seconds))
    with httpx.Client(
        headers={"User-Agent": USER_AGENT}, follow_redirects=True, timeout=20
    ) as client:
        response = client.get(url)
        response.raise_for_status()
    if len(response.content) > MAX_RESPONSE_BYTES:
        raise ValueError("response exceeds 10 MiB")
    content_type = response.headers.get("content-type", "").split(";", 1)[0]
    if content_type not in {"text/html", "text/plain", "text/markdown", "application/json"}:
        raise ValueError(f"unsupported content type: {content_type}")
    if content_type == "text/html":
        parser = TextExtractor()
        parser.feed(response.text)
        text = parser.text()
    else:
        text = response.text
    sensitive = [name for name, pattern in SENSITIVE_PATTERNS.items() if pattern.search(text)]
    if sensitive:
        raise ValueError(f"sensitive material detected: {sensitive}")
    digest = hashlib.sha256(text.encode()).hexdigest()
    relative = Path("data/raw") / source["source_id"] / "web-page.txt"
    destination = root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    record = {
        "document_id": f"DOC-{digest[:20]}",
        "source_id": source["source_id"],
        "canonical_url": str(response.url),
        "repository_url": None,
        "commit_sha": None,
        "relative_path": "web-page.txt",
        "raw_path": str(relative),
        "content_sha256": digest,
        "mime_type": "text/plain",
        "published_at": source.get("published_at"),
        "observed_at": datetime.now(UTC).isoformat(),
        "extractor_version": "html-text-v1",
        "status": "accepted",
    }
    manifest = root / "data/registry/documents.jsonl"
    records = (
        [
            json.loads(line)
            for line in manifest.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if manifest.exists()
        else []
    )
    records = [
        item
        for item in records
        if not (
            item["source_id"] == source["source_id"] and item["relative_path"] == "web-page.txt"
        )
    ]
    records.append(record)
    records.sort(key=lambda item: (item["source_id"], item["relative_path"]))
    manifest.write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in records), encoding="utf-8"
    )
    return {
        "source_id": source["source_id"],
        "bytes": len(text.encode()),
        "sha256": digest,
        "url": str(response.url),
    }


def _assert_robots_allowed(url: str) -> None:
    parts = urlsplit(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
    except OSError as error:
        raise RuntimeError(f"could not verify robots.txt for {url}") from error
    if not parser.can_fetch(USER_AGENT, url):
        raise PermissionError(f"robots.txt disallows collection: {url}")
