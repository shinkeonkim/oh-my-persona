from dataclasses import dataclass
from typing import Literal

InboxStatus = Literal["accepted", "rejected", "review"]


@dataclass(frozen=True, slots=True)
class InboxFinding:
    path: str
    status: InboxStatus
    sha256: str
    mime: str
    reasons: tuple[str, ...] = ()
