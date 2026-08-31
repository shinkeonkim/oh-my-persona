from __future__ import annotations

import re
from typing import Final

SENSITIVE_PATTERNS: Final = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "korean_rrn": re.compile(r"\b\d{6}-[1-4]\d{6}\b"),
}

PRIVATE_QUERY_TERMS: Final = (
    "주민등록번호",
    "전화번호",
    "집주소",
    "비밀번호",
    "API 키",
    "private key",
)
