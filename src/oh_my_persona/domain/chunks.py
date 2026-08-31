from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Chunk:
    chunk_id: str
    source_path: str
    ordinal: int
    text: str
    content_sha256: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def chunk_text(text: str, source_path: str, max_chars: int = 750) -> list[Chunk]:
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    chunks: list[Chunk] = []
    buffer = ""
    for block in blocks:
        if buffer and len(buffer) + len(block) + 2 > max_chars:
            chunks.append(_make_chunk(source_path, len(chunks), buffer))
            buffer = block
        else:
            buffer = f"{buffer}\n\n{block}".strip()
    if buffer:
        chunks.append(_make_chunk(source_path, len(chunks), buffer))
    return chunks


def _make_chunk(source_path: str, ordinal: int, text: str) -> Chunk:
    digest = hashlib.sha256(text.encode()).hexdigest()
    stable_id = hashlib.sha256(f"{source_path}:{ordinal}:{digest}".encode()).hexdigest()[:20]
    return Chunk(f"CHK-{stable_id}", source_path, ordinal, text, digest)
