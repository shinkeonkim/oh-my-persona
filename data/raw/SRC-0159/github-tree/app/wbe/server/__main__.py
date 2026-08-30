"""브라우저를 시험해 볼 작은 웹 서버.

주제별 게시판 · 로그인 세션 · CSRF 논스 · CORS 엔드포인트를 담고 있다.
글은 파일에 남으므로 서버를 다시 켜도 사라지지 않는다.

    wbe browse.server            # http://localhost:8000/
"""

import html
import os
import random
import socket
import sys
import time
import urllib.parse

HOST, PORT = "", 8000
SESSION_MAX_AGE = 60 * 60
STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "board.txt")

# 토큰 -> {"data": {...}, "expires": 시각}
SESSIONS = {}

LOGINS = {"crashoverride": "0cool", "cerealkiller": "emmanuel"}


def e(text):
    return html.escape(str(text), quote=True)


def new_token():
    return str(random.random())[2:]


def normalize(topic):
    topic = (topic or "").strip().strip("/")
    if "/" in topic or "\t" in topic or "\n" in topic:
        return ""
    return topic


# ---------------------------------------------------------------------- #
# 저장
# ---------------------------------------------------------------------- #

class Board:
    """주제 -> 글 목록. 파일 한 줄이 글 하나다."""

    def __init__(self, path=STORE):
        self.path = path
        self.topics = {}
        self.load()

    def load(self):
        self.topics = {}
        if not self.path or not os.path.exists(self.path):
            return
        with open(self.path, encoding="utf8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line:
                    continue
                topic, _, entry = line.partition("\t")
                self.topics.setdefault(topic, [])
                if entry:
                    self.topics[topic].append(entry)

    def save(self):
        if not self.path:
            return
        with open(self.path, "w", encoding="utf8") as f:
            for topic, entries in self.topics.items():
                if not entries:
                    f.write(topic + "\t\n")      # 빈 주제도 남긴다
                for entry in entries:
                    f.write("%s\t%s\n" % (topic, entry))

    def add_topic(self, topic):
        topic = normalize(topic)
        if not topic:
            return None
        self.topics.setdefault(topic, [])
        self.save()
        return topic

    def add_entry(self, topic, text):
        topic = normalize(topic)
        text = (text or "").strip()
        if not topic or not text:
            return False
        self.topics.setdefault(topic, []).append(text)
        self.save()
        return True

    def has(self, topic):
        return normalize(topic) in self.topics

    def entries(self, topic):
        return self.topics.get(normalize(topic), [])

    def names(self):
        return sorted(self.topics)


BOARD = Board()


# ---------------------------------------------------------------------- #
# 세션
# ---------------------------------------------------------------------- #

def expire_sessions(now=None):
    """지난 세션을 지운다. 안 하면 SESSIONS 가 끝없이 자란다."""
    now = time.time() if now is None else now
    for token in [t for t, s in SESSIONS.items() if s["expires"] <= now]:
        del SESSIONS[token]


def get_session(token, now=None):
    now = time.time() if now is None else now
    expire_sessions(now)
    if token not in SESSIONS:
        SESSIONS[token] = {"data": {}, "expires": now + SESSION_MAX_AGE}
    return SESSIONS[token]["data"]


def touch_session(token, now=None):
    now = time.time() if now is None else now
    if token in SESSIONS:
        SESSIONS[token]["expires"] = now + SESSION_MAX_AGE


# ---------------------------------------------------------------------- #
# 페이지
# ---------------------------------------------------------------------- #

def home_page(session):
    items = "".join('<li><a href="/{0}">{1}</a></li>'.format(
        urllib.parse.quote(t), e(t)) for t in BOARD.names())
    who = session.get("user")
    header = "<p>%s 님으로 로그인했습니다</p>" % e(who) if who \
        else '<p><a href="/login">로그인</a></p>'
    return ("<!doctype html><html><head><title>게시판</title></head><body>"
            "<h1>게시판</h1>" + header +
            "<ul>" + (items or "<li>아직 주제가 없습니다</li>") + "</ul>"
            '<form action="/" method="post">'
            '<p>새 주제: <input name="topic" value=""> '
            "<button>만들기</button></p></form>"
            "</body></html>")


def topic_page(session, topic):
    items = "".join("<li>%s</li>" % e(x) for x in BOARD.entries(topic))
    path = "/" + urllib.parse.quote(normalize(topic))
    form = ""
    if "user" in session:
        nonce = new_token()
        session["nonce"] = nonce
        form = ('<form action="{0}" method="post">'
                '<p><input name="guest" value=""> '
                '<input name="nonce" type="hidden" value="{1}"> '
                '<input name="sign" type="checkbox" value="yes"> 서명 '
                "<button>남기기</button></p></form>").format(path, e(nonce))
    else:
        form = '<p><a href="/login">로그인해서 글 남기기</a></p>'
    return ("<!doctype html><html><head><title>{0}</title></head><body>"
            "<h1>{0}</h1><ul>{1}</ul>{2}"
            '<p><a href="/">주제 목록</a></p></body></html>').format(
        e(normalize(topic)), items or "<li>아직 글이 없습니다</li>", form)


def login_form():
    return ("<!doctype html><html><head><title>로그인</title></head><body>"
            '<form action="/" method="post">'
            '<p>사용자: <input name="username" value=""></p>'
            '<p>암호: <input name="password" type="password" value=""></p>'
            "<p><button>로그인</button></p></form></body></html>")


def not_found(url, method):
    return ("<!doctype html><html><body><h1>{} {} 를 찾을 수 없습니다</h1>"
            '<p><a href="/">주제 목록</a></p></body></html>').format(
        e(method), e(url))


# ---------------------------------------------------------------------- #
# 요청 처리
# ---------------------------------------------------------------------- #

def form_decode(body):
    params = {}
    for field in (body or "").split("&"):
        if not field:
            continue
        name, _, value = field.partition("=")
        params[urllib.parse.unquote_plus(name)] = \
            urllib.parse.unquote_plus(value)
    return params


def do_login(session, params):
    username, password = params.get("username"), params.get("password")
    if username in LOGINS and LOGINS[username] == password:
        session["user"] = username
        return True
    return False


def add_entry(session, topic, params):
    if "user" not in session:
        return False
    if params.get("nonce") != session.get("nonce"):
        return False                    # CSRF 방어
    text = (params.get("guest") or "").strip()
    if not text:
        return False
    if params.get("sign") == "yes":
        text += " (서명함)"
    return BOARD.add_entry(topic, "%s — %s" % (text, session["user"]))


def do_request(session, method, url, headers, body):
    """(상태, 본문, 추가 헤더)."""
    extra = {}
    path = urllib.parse.unquote(url)

    if path == "/cors":                 # 이 주소만 교차 출처를 허락한다
        origin = headers.get("origin")
        if origin:
            extra["Access-Control-Allow-Origin"] = origin
            extra["Access-Control-Allow-Credentials"] = "true"
        return "200 OK", '{"ok": true}', extra
    if path == "/nocors":
        return "200 OK", '{"ok": true}', extra

    if method == "POST":
        params = form_decode(body)
        if path == "/":
            if "username" in params:
                do_login(session, params)
            else:
                BOARD.add_topic(params.get("topic", ""))
            return "200 OK", home_page(session), extra
        topic = normalize(path)
        if topic:
            add_entry(session, topic, params)
            return "200 OK", topic_page(session, topic), extra
        return "404 Not Found", not_found(url, method), extra

    if path == "/":
        return "200 OK", home_page(session), extra
    if path == "/login":
        return "200 OK", login_form(), extra
    topic = normalize(path)
    if BOARD.has(topic):
        return "200 OK", topic_page(session, topic), extra
    return "404 Not Found", not_found(url, method), extra


def handle_connection(conx):
    req = conx.makefile("b")
    line = req.readline().decode("utf8")
    parts = line.split(" ", 2)
    if len(parts) < 2:
        # 요청 줄이 없거나 모양이 틀렸다. 포트가 열렸는지만 보고 끊는
        # 연결이 흔하다 — 그것 때문에 서버가 죽으면 안 된다.
        conx.close()
        return
    method, url = parts[0], parts[1]

    headers = {}
    while True:
        line = req.readline().decode("utf8")
        if line in ("\r\n", "\n", ""):
            break
        header, _, value = line.partition(":")
        headers[header.casefold()] = value.strip()

    body = None
    if "content-length" in headers:
        body = req.read(int(headers["content-length"])).decode("utf8")

    if "cookie" in headers:
        token = headers["cookie"].split("=", 1)[1].split(";")[0]
    else:
        token = new_token()
    session = get_session(token)
    touch_session(token)

    status, page, extra = do_request(session, method, url, headers, body)
    data = page.encode("utf8")

    response = "HTTP/1.0 {}\r\n".format(status)
    if "cookie" not in headers:
        response += ("Set-Cookie: token={}; SameSite=Lax; HttpOnly; "
                     "Max-Age={}\r\n").format(token, SESSION_MAX_AGE)
    for name, value in extra.items():
        response += "{}: {}\r\n".format(name, value)
    response += "Content-Length: {}\r\n".format(len(data))
    response += "Content-Type: text/html; charset=utf-8\r\n"
    response += "Referrer-Policy: no-referrer-when-downgrade\r\n"
    # HTTP/1.0 이라 요청마다 끊는다. 안 적으면 브라우저가 소켓을 재사용한다.
    response += "Connection: close\r\n\r\n"
    conx.send(response.encode("utf8") + data)
    conx.close()


def main(argv):
    port = int(argv[0]) if argv else PORT
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM,
                      proto=socket.IPPROTO_TCP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, port))
    s.listen()
    print("http://localhost:%d/ 에서 듣고 있습니다" % port)
    while True:
        conx, addr = s.accept()
        # 연결 하나가 잘못돼도 서버는 계속 돈다
        try:
            handle_connection(conx)
        except Exception as e:
            print("연결 처리 실패 (%s): %s" % (addr[0] if addr else "?", e),
                  file=sys.stderr)
            try:
                conx.close()
            except OSError:
                pass


if __name__ == "__main__":
    main(sys.argv[1:])
