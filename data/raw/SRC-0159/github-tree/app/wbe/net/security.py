"""전송 보안 — 인증서, 콘텐츠 보안 정책, 프레임 삽입 허용."""

REFERRER_POLICIES = {"no-referrer", "same-origin", "no-referrer-when-downgrade"}


class CertificateError(Exception):
    """서버 인증서를 믿을 수 없다."""


def parse_csp(header):
    """'default-src http://a http://b' -> ['http://a', 'http://b']

    정책이 없으면 None (= 아무 곳이나 허용).
    """
    if not header:
        return None
    parts = header.split()
    if len(parts) < 2 or parts[0].casefold() != "default-src":
        return None
    return parts[1:]


def allowed_by_csp(allowed_origins, url):
    return allowed_origins is None or url.origin() in allowed_origins


def frame_allowed(headers, parent_origin, target_origin):
    """X-Frame-Options: 이 응답을 iframe 안에 넣어도 되는가."""
    value = (headers or {}).get("x-frame-options", "").strip().casefold()
    if not value:
        return True
    if value == "deny":
        return False
    if value == "sameorigin":
        return parent_origin == target_origin
    return True


def cors_allows(response_headers, requesting_origin):
    """Access-Control-Allow-Origin 을 보고 교차 출처 응답을 넘겨줄지 정한다."""
    allow = (response_headers or {}).get("access-control-allow-origin", "")
    return allow in ("*", requesting_origin)


def referrer_policy_of(headers):
    policy = (headers or {}).get("referrer-policy", "").casefold()
    return policy if policy in REFERRER_POLICIES else None
