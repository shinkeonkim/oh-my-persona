from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TurnstileVerifier:
    secret_key: str | None = None
    site_key: str | None = None

    @classmethod
    def from_environment(cls) -> TurnstileVerifier:
        return cls(
            secret_key=os.environ.get("PERSONA_TURNSTILE_SECRET_KEY"),
            site_key=os.environ.get("PERSONA_TURNSTILE_SITE_KEY"),
        )

    @property
    def enabled(self) -> bool:
        return bool(self.secret_key and self.site_key)

    def verify(self, token: str | None, remote_ip: str) -> bool:
        if not self.enabled:
            return True
        if not token or not self.secret_key:
            return False
        body = urllib.parse.urlencode(
            {"secret": self.secret_key, "response": token, "remoteip": remote_ip}
        ).encode()
        request = urllib.request.Request(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify", data=body, method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=8) as response:
                result: dict[str, object] = json.loads(response.read())
            return result.get("success") is True
        except OSError:
            return False
