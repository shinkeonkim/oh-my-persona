"""URL 파싱과 HTTP 요청.

지원하는 스킴: http, https, file, data, about, view-source.

요청 한 번에 다음이 모두 걸린다.
    keep-alive 소켓 재사용 · chunked/gzip 해제 · 리다이렉트 추적 ·
    Cache-Control 캐시 · 쿠키 · Origin · Referer · 인증서 오류
"""

import base64
import gzip
import socket
import ssl
import time
import urllib.parse

from wbe.net import cookies as cookiejar
from wbe.net.security import CertificateError

MAX_REDIRECTS = 10
USER_AGENT = "wbe-ko/1.0"

# (스킴, 호스트, 포트) 별로 살아 있는 소켓
SOCKETS = {}

# URL 문자열 -> (본문, 만료시각). 만료시각 None 이면 만료 없음.
CACHE = {}

# about:<이름> 을 만들어 주는 함수들. 다른 모듈이 등록한다.
ABOUT_PAGES = {}


def register_about(name, builder):
    """about:bookmarks 처럼 브라우저가 만들어 내는 페이지를 등록한다."""
    ABOUT_PAGES[name] = builder


class URL:
    def __init__(self, url):
        self.socket = None
        self.fragment = None
        self.response_headers = {}

        # #프래그먼트는 떼어서 따로 들고 다닌다
        if "#" in url:
            url, self.fragment = url.split("#", 1)
            self.fragment = self.fragment or None

        # view-source: 는 다른 URL 을 감싼다
        self.view_source = False
        if url.startswith("view-source:"):
            self.view_source = True
            url = url[len("view-source:"):]

        if url.startswith("about:"):
            self.scheme = "about"
            self.path = url[len("about:"):] or "blank"
            return

        if url.startswith("data:"):
            self.scheme = "data"
            mediatype, _, self.data = url[len("data:"):].partition(",")
            self.mediatype = mediatype or "text/plain"
            return

        self.scheme, _, url = url.partition("://")
        assert self.scheme in ("http", "https", "file"), \
            "지원하지 않는 스킴입니다: " + self.scheme

        if self.scheme == "file":
            self.host = ""
            self.path = url if url.startswith("/") else "/" + url
            return

        self.port = 80 if self.scheme == "http" else 443
        if "/" not in url:
            url = url + "/"
        self.host, _, path = url.partition("/")
        self.path = "/" + path
        if ":" in self.host:
            self.host, _, port = self.host.partition(":")
            self.port = int(port)

    # ------------------------------------------------------------------ #
    # 정체
    # ------------------------------------------------------------------ #

    def origin(self):
        """호스트가 없는 스킴은 불투명 출처다."""
        if getattr(self, "host", None) is None or self.scheme in \
                ("about", "data", "file"):
            return "null"
        return "{}://{}:{}".format(self.scheme, self.host, self.port)

    def is_secure(self):
        return self.scheme == "https"

    def same_page(self, other):
        """프래그먼트만 다른가?"""
        return self.base_str() == other.base_str()

    def base_str(self):
        """프래그먼트를 뺀 주소."""
        if self.scheme == "about":
            return "about:" + self.path
        if self.scheme == "data":
            return "data:{},...".format(self.mediatype)
        if self.scheme == "file":
            return "file://{}".format(self.path)
        return "{}://{}:{}{}".format(self.scheme, self.host, self.port,
                                     self.path)

    def __str__(self):
        return self.base_str() + ("#" + self.fragment if self.fragment else "")

    __repr__ = __str__

    # ------------------------------------------------------------------ #
    # 상대 주소 풀기
    # ------------------------------------------------------------------ #

    def resolve(self, url):
        """상대 주소를 절대 주소로. '#id' 는 같은 페이지의 다른 곳이다."""
        if url.startswith("#"):
            out = URL(self.base_str())
            out.fragment = url[1:] or None
            return out
        # 절대 주소는 원문 그대로 새로 만든다. str() 을 거치면 data: 의
        # 내용이 사라진다.
        if "://" in url or url.startswith(("about:", "data:", "view-source:")):
            return URL(url)
        if self.scheme in ("about", "data"):
            return URL(url)
        if not url.startswith("/"):
            dir_, _, _ = self.path.rpartition("/")
            while url.startswith("../"):
                url = url[3:]
                if "/" in dir_:
                    dir_, _, _ = dir_.rpartition("/")
            url = dir_ + "/" + url
        return URL("{}://{}:{}{}".format(self.scheme, self.host, self.port,
                                         url))

    def with_query(self, query):
        """경로 뒤에 ?질의 를 붙인 새 URL. GET 폼 제출에 쓴다."""
        path = self.path.split("?", 1)[0]
        return URL("{}://{}:{}{}?{}".format(self.scheme, self.host, self.port,
                                            path, query))

    # ------------------------------------------------------------------ #
    # 요청
    # ------------------------------------------------------------------ #

    def request(self, referrer=None, payload=None,
                redirects_left=MAX_REDIRECTS, origin=None,
                referrer_policy=None, top_level=True):
        self.response_headers = {}

        if self.scheme == "about":
            builder = ABOUT_PAGES.get(self.path)
            return builder() if builder else ""
        if self.scheme == "data":
            # data: URL 의 내용은 퍼센트 인코딩돼 있다 (RFC 2397)
            return urllib.parse.unquote(self.data)
        if self.scheme == "file":
            with open(self.path, encoding="utf8") as f:
                return f.read()

        # GET 만 캐시한다. POST 는 서버 상태를 바꾸므로 다시 보낸다.
        if payload is None:
            cached = self._cache_read()
            if cached is not None:
                return cached

        try:
            s = self._connect()
        except (ssl.SSLCertVerificationError, ssl.SSLError) as e:
            raise CertificateError(str(e))

        s.send(self._request_bytes(payload, referrer, referrer_policy,
                                   origin, top_level))
        response = s.makefile("rb", newline="\r\n")
        _, status, _ = self._read_status(response)
        headers = self._read_headers(response)

        for header in headers.get("set-cookie-all", []):
            cookiejar.store_cookie(self.host, header)

        if 300 <= status < 400 and "location" in headers:
            self._finish(s, headers, body=b"")
            if redirects_left <= 0:
                raise Exception("리다이렉트가 너무 많이 이어집니다")
            # POST 뒤의 리다이렉트는 GET 으로 따라간다
            return self.resolve(headers["location"]).request(
                referrer, None, redirects_left - 1, origin,
                referrer_policy, top_level)

        body = self._read_body(response, headers)
        self._finish(s, headers, body)
        self.response_headers = headers
        text = body.decode("utf8", "replace")

        if status == 200 and payload is None:
            self._cache_write(headers, text)
        return text

    def request_bytes(self):
        """이미지처럼 글자가 아닌 것을 받아 온다."""
        if self.scheme == "data":
            if self.mediatype.casefold().endswith(";base64"):
                return base64.b64decode(self.data)
            return urllib.parse.unquote_to_bytes(self.data)
        if self.scheme == "file":
            with open(self.path, "rb") as f:
                return f.read()
        return self.request().encode("utf8", "surrogateescape")

    # -- 요청 조립 ----------------------------------------------------- #

    def referrer_value(self, referrer, policy):
        """Referrer-Policy 를 지켜 Referer 헤더 값을 정한다."""
        if referrer is None:
            return None
        policy = (policy or "no-referrer-when-downgrade").casefold()
        if policy == "no-referrer":
            return None
        if policy == "same-origin" and referrer.origin() != self.origin():
            return None
        if policy == "no-referrer-when-downgrade" \
                and referrer.is_secure() and not self.is_secure():
            return None
        return str(referrer)

    def _request_bytes(self, payload, referrer, referrer_policy, origin,
                       top_level):
        headers = {
            "Host": self.host,
            "Connection": "keep-alive",
            "User-Agent": USER_AGENT,
            "Accept-Encoding": "gzip",
        }
        method = "POST" if payload is not None else "GET"
        data = payload.encode("utf8") if payload is not None else b""
        if payload is not None:
            headers["Content-Length"] = str(len(data))
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        cookie = cookiejar.cookie_header(self.host, top_level=top_level)
        if cookie:
            headers["Cookie"] = cookie
        if origin is not None:
            headers["Origin"] = origin
        ref = self.referrer_value(referrer, referrer_policy)
        if ref:
            headers["Referer"] = ref

        lines = ["{} {} HTTP/1.1".format(method, self.path)]
        lines += ["{}: {}".format(k, v) for k, v in headers.items()]
        return ("\r\n".join(lines) + "\r\n\r\n").encode("utf8") + data

    def _connect(self):
        key = (self.scheme, self.host, self.port)
        s = SOCKETS.get(key)
        if s is None:
            s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM,
                              proto=socket.IPPROTO_TCP)
            s.connect((self.host, self.port))
            if self.scheme == "https":
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self.host)
            SOCKETS[key] = s
        self.socket = s
        return s

    def _finish(self, s, headers, body):
        """Connection: close 이거나 본문 길이를 모르면 소켓을 버린다."""
        key = (self.scheme, self.host, self.port)
        if headers.get("connection", "").lower() == "close" or \
                ("content-length" not in headers and
                 headers.get("transfer-encoding", "").lower() != "chunked"):
            SOCKETS.pop(key, None)
            try:
                s.close()
            except OSError:
                pass

    # -- 응답 해석 ----------------------------------------------------- #

    @staticmethod
    def _read_status(response):
        line = response.readline().decode("utf8")
        version, _, rest = line.strip().partition(" ")
        status, _, explanation = rest.partition(" ")
        return version, int(status), explanation

    @staticmethod
    def _read_headers(response):
        """Set-Cookie 는 여러 번 올 수 있어서 따로 모은다."""
        out, all_cookies = {}, []
        while True:
            line = response.readline()
            if line in (b"\r\n", b"\n", b""):
                break
            header, _, value = line.decode("utf8").partition(":")
            header = header.casefold()
            value = value.strip()
            if header == "set-cookie":
                all_cookies.append(value)
            out[header] = value
        if all_cookies:
            out["set-cookie-all"] = all_cookies
        return out

    def _read_body(self, response, headers):
        """길이만큼만 읽고, chunked 와 gzip 을 푼다."""
        encoding = headers.get("transfer-encoding", "").lower()
        if encoding == "chunked":
            body = self._read_chunked(response)
        elif "content-length" in headers:
            body = response.read(int(headers["content-length"]))
        else:
            body = response.read()

        if headers.get("content-encoding", "").lower() == "gzip":
            body = gzip.decompress(body)
        return body

    @staticmethod
    def _read_chunked(response):
        out = b""
        while True:
            size = int(response.readline().split(b";")[0].strip() or b"0", 16)
            if size == 0:
                break
            out += response.read(size)
            response.readline()          # 청크 뒤의 CRLF
        while True:                      # 트레일러 헤더
            line = response.readline()
            if line in (b"\r\n", b"\n", b""):
                break
        return out

    # -- 캐시 ----------------------------------------------------------- #

    def _cache_read(self):
        entry = CACHE.get(str(self))
        if not entry:
            return None
        body, expires = entry
        if expires is not None and time.time() > expires:
            del CACHE[str(self)]
            return None
        return body

    def _cache_write(self, headers, body):
        """no-store 면 저장하지 않고, max-age 외의 지시어가 있어도 저장하지 않는다."""
        control = headers.get("cache-control", "").strip().lower()
        if not control:
            CACHE[str(self)] = (body, None)
            return
        expires = None
        for directive in [d.strip() for d in control.split(",")]:
            if directive == "no-store":
                return
            if directive.startswith("max-age="):
                try:
                    expires = time.time() + int(directive[len("max-age="):])
                except ValueError:
                    return
            else:
                return          # 모르는 지시어가 있으면 캐시하지 않는다
        CACHE[str(self)] = (body, expires)


# ---------------------------------------------------------------------- #
# 주소 다루기
# ---------------------------------------------------------------------- #

def parse_url(text):
    """잘못된 주소면 죽지 않고 about:blank 으로 대신한다."""
    try:
        return URL(text)
    except Exception:
        return URL("about:blank")


def resolve(base, href):
    """상대 주소를 푼다. base 가 없으면 절대 주소로만 본다."""
    if base is None:
        return URL(href)
    return base.resolve(href)


def percent_encode(text):
    out = []
    for byte in text.encode("utf8"):
        c = chr(byte)
        # ASCII 범위만 안전하다. 0x80 이상은 chr() 이 라틴-1 글자를 주는데
        # 그것도 isalnum() 을 통과하므로 여기서 걸러야 이중 인코딩을 막는다.
        if (byte < 128 and c.isalnum()) or c in "-_.~":
            out.append(c)
        elif c == " ":
            out.append("+")
        else:
            out.append("%%%02X" % byte)
    return "".join(out)


def form_encode(pairs):
    return "&".join("%s=%s" % (percent_encode(k), percent_encode(v))
                    for k, v in pairs)


def form_decode(body):
    params = {}
    for field in (body or "").split("&"):
        if not field:
            continue
        name, _, value = field.partition("=")
        params[urllib.parse.unquote_plus(name)] = \
            urllib.parse.unquote_plus(value)
    return params
