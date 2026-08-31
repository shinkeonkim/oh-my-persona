from __future__ import annotations

from typing import Self

from oh_my_persona.infrastructure.security import TurnstileVerifier


class _Response:
    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        pass

    def read(self) -> bytes:
        return b'{"success":true}'


def test_disabled_turnstile_allows_requests() -> None:
    assert TurnstileVerifier().verify(None, "192.0.2.1") is True


def test_enabled_turnstile_requires_and_verifies_token(monkeypatch) -> None:
    verifier = TurnstileVerifier(secret_key="secret", site_key="site")
    assert verifier.verify(None, "192.0.2.1") is False
    monkeypatch.setattr("urllib.request.urlopen", lambda *_args, **_kwargs: _Response())
    assert verifier.verify("valid-token", "192.0.2.1") is True
