"""쿠키 저장고.

호스트마다 이름 -> (값, 매개변수) 를 들고 있다. `SameSite` 로 교차 사이트
요청에서 빼고, `HttpOnly` 로 스크립트에서 감추고, `Max-Age`/`Expires` 로
만료시킨다.
"""

import email.utils
import time

# 호스트 -> {이름: (값, 매개변수)}
COOKIE_JAR = {}


def parse_cookie(header):
    """'k=v; SameSite=Lax; HttpOnly' -> (k, v, 매개변수)"""
    parts = header.split(";")
    key, _, value = parts[0].strip().partition("=")
    params = {}
    for param in parts[1:]:
        name, _, val = param.strip().partition("=")
        params[name.strip().casefold()] = val.strip()
    return key.strip(), value.strip(), params


def cookie_expiry(params, now=None):
    """Max-Age 가 Expires 보다 우선한다. 둘 다 없으면 세션 쿠키."""
    now = time.time() if now is None else now
    if "max-age" in params:
        try:
            return now + float(params["max-age"])
        except ValueError:
            return None
    if "expires" in params:
        try:
            return email.utils.parsedate_to_datetime(
                params["expires"]).timestamp()
        except (TypeError, ValueError):
            return None
    return None


def store_cookie(host, header, now=None):
    key, value, params = parse_cookie(header)
    expires = cookie_expiry(params, now)
    if expires is not None:
        params["__expires"] = expires
        if expires <= (time.time() if now is None else now):
            COOKIE_JAR.get(host, {}).pop(key, None)   # 이미 지난 쿠키는 삭제
            return key, value, params
    COOKIE_JAR.setdefault(host, {})[key] = (value, params)
    return key, value, params


def live_cookies(host, now=None):
    """만료된 것은 저장고에서 지우고 나머지를 돌려준다."""
    now = time.time() if now is None else now
    jar = COOKIE_JAR.get(host, {})
    for key in [k for k, (_, p) in jar.items()
                if p.get("__expires") is not None and p["__expires"] <= now]:
        del jar[key]
    return jar


def cookie_header(host, top_level=True, script_visible=False, now=None):
    """보낼 Cookie 헤더 값. 보낼 것이 없으면 None.

    top_level 이 False 면 교차 사이트 요청이므로 SameSite=Lax 쿠키를 뺀다.
    script_visible 이면 document.cookie 로 읽는 것이므로 HttpOnly 를 뺀다.
    """
    out = []
    for key, (value, params) in live_cookies(host, now).items():
        if not top_level and params.get("samesite", "lax").casefold() == "lax":
            continue
        if script_visible and "httponly" in params:
            continue
        out.append("%s=%s" % (key, value))
    return "; ".join(out) if out else None


def clear():
    COOKIE_JAR.clear()
