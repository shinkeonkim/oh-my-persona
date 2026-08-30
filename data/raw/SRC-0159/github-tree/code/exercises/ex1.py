"""1장 연습문제 구현 (1-1 ~ 1-9).

lab1.py 를 건드리지 않고, 그 위에 연습문제 기능을 얹은 URL/show 를 새로 정의한다.
다음 장의 연습문제 파일(ex2.py)은 이 모듈에서 import 해 이어서 발전시킨다.

    python3 ex1.py https://browser.engineering/
    python3 ex1.py view-source:https://example.org/
    python3 ex1.py file:///etc/hosts
    python3 ex1.py 'data:text/html,<b>Hello</b> &lt;world&gt;'

구현한 연습문제
    1-1 HTTP/1.1      요청 헤더를 딕셔너리로 관리, Connection/User-Agent 전송
    1-2 File URLs     file:// 스킴
    1-3 data          data:text/html, 스킴
    1-4 Entities      &lt; &gt; &amp; &quot; &#39; 해석
    1-5 view-source   렌더링 대신 HTML 소스 출력
    1-6 Keep-alive    소켓 재사용 + Content-Length 만큼만 읽기
    1-7 Redirects     3xx Location 추적 (순환 방지)
    1-8 Caching       Cache-Control 의 no-store / max-age 지원
    1-9 Compression   Accept-Encoding: gzip + chunked 전송 해제
"""

import gzip
import socket
import ssl
import sys
import time

# 연습문제 1-6: (스킴, 호스트, 포트) 별로 살아 있는 소켓을 재사용한다.
SOCKETS = {}

# 연습문제 1-8: URL 문자열 -> (본문, 만료시각). 만료시각 None 이면 만료 없음.
CACHE = {}

MAX_REDIRECTS = 10

# 연습문제 1-4
ENTITIES = {
    "&lt;": "<",
    "&gt;": ">",
    "&amp;": "&",
    "&quot;": '"',
    "&#39;": "'",
}


class URL:
    def __init__(self, url):
        self.socket = None

        # 연습문제 1-5: view-source: 는 다른 URL 을 감싼다.
        self.view_source = False
        if url.startswith("view-source:"):
            self.view_source = True
            url = url[len("view-source:"):]

        # 연습문제 1-3: data:<mediatype>,<data>
        if url.startswith("data:"):
            self.scheme = "data"
            mediatype, _, self.data = url[len("data:"):].partition(",")
            self.mediatype = mediatype or "text/plain"
            return

        self.scheme, _, url = url.partition("://")
        assert self.scheme in ("http", "https", "file"), \
            "지원하지 않는 스킴입니다: " + self.scheme

        # 연습문제 1-2: file:///path/to/file — 호스트가 없고 경로만 있다.
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
    # 요청
    # ------------------------------------------------------------------ #

    def request(self, redirects_left=MAX_REDIRECTS):
        if self.scheme == "data":
            return self.data                       # 1-3
        if self.scheme == "file":
            with open(self.path, encoding="utf8") as f:
                return f.read()                    # 1-2

        cached = self._cache_read()                # 1-8
        if cached is not None:
            return cached

        s = self._connect()                        # 1-6
        s.send(self._request_bytes())

        response = s.makefile("rb", newline="\r\n")
        version, status, explanation = self._read_status(response)
        headers = self._read_headers(response)

        # 연습문제 1-7: 3xx 는 Location 을 따라간다.
        if 300 <= status < 400 and "location" in headers:
            self._finish(s, headers, body=b"")
            if redirects_left <= 0:
                raise Exception("리다이렉트가 너무 많이 이어집니다")
            return self._redirect(headers["location"], redirects_left)

        body = self._read_body(response, headers)  # 1-6 / 1-9
        self._finish(s, headers, body)
        text = body.decode("utf8", "replace")

        if status == 200:
            self._cache_write(headers, text)       # 1-8
        return text

    # -- 요청 조립 ----------------------------------------------------- #

    def _request_bytes(self):
        """연습문제 1-1: 헤더를 딕셔너리로 모아 두면 나중에 추가하기 쉽다."""
        headers = {
            "Host": self.host,
            "Connection": "keep-alive",   # 1-6 (1-1 의 close 대신)
            "User-Agent": "wbe-ko/1.0",   # 1-1
            "Accept-Encoding": "gzip",    # 1-9
        }
        lines = ["GET {} HTTP/1.1".format(self.path)]
        lines += ["{}: {}".format(k, v) for k, v in headers.items()]
        return ("\r\n".join(lines) + "\r\n\r\n").encode("utf8")

    def _connect(self):
        key = (self.scheme, self.host, self.port)
        s = SOCKETS.get(key)
        if s is None:
            s = socket.socket(family=socket.AF_INET,
                              type=socket.SOCK_STREAM,
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
        headers = {}
        while True:
            line = response.readline().decode("utf8")
            if line in ("\r\n", "\n", ""):
                break
            header, _, value = line.partition(":")
            headers[header.casefold()] = value.strip()
        return headers

    def _read_body(self, response, headers):
        """연습문제 1-6 + 1-9: 길이만큼만 읽고, chunked 와 gzip 을 푼다."""
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

    # -- 리다이렉트 / 캐시 --------------------------------------------- #

    def _redirect(self, location, redirects_left):
        if location.startswith("/"):
            target = "{}://{}:{}{}".format(
                self.scheme, self.host, self.port, location)
        elif "://" not in location:
            base = self.path.rsplit("/", 1)[0]
            target = "{}://{}:{}{}/{}".format(
                self.scheme, self.host, self.port, base, location)
        else:
            target = location
        nxt = URL(target)
        nxt.view_source = self.view_source
        return nxt.request(redirects_left - 1)

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
        directives = [d.strip() for d in control.split(",")]
        expires = None
        for d in directives:
            if d == "no-store":
                return
            if d.startswith("max-age="):
                try:
                    expires = time.time() + int(d[len("max-age="):])
                except ValueError:
                    return
            else:
                return          # 모르는 지시어가 있으면 캐시하지 않는다
        CACHE[str(self)] = (body, expires)

    def __repr__(self):
        if self.scheme == "data":
            return "data:{},...".format(self.mediatype)
        if self.scheme == "file":
            return "file://{}".format(self.path)
        return "{}://{}:{}{}".format(self.scheme, self.host, self.port, self.path)


# ---------------------------------------------------------------------- #
# 출력
# ---------------------------------------------------------------------- #

def decode_entities(text):
    """연습문제 1-4."""
    for entity, char in ENTITIES.items():
        text = text.replace(entity, char)
    return text


def lex(body):
    """태그를 걷어내고 텍스트만 남긴다 (엔티티 해석 포함)."""
    out = []
    in_tag = False
    buffer = ""
    for c in body:
        if c == "<":
            in_tag = True
            out.append(decode_entities(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
        elif not in_tag:
            buffer += c
    out.append(decode_entities(buffer))
    return "".join(out)


def show(body, view_source=False):
    """연습문제 1-5: view-source 면 소스를 그대로 보여 준다."""
    print(body if view_source else lex(body), end="")


def load(url):
    show(url.request(), url.view_source)


if __name__ == "__main__":
    load(URL(sys.argv[1] if len(sys.argv) > 1 else "https://example.org/"))
