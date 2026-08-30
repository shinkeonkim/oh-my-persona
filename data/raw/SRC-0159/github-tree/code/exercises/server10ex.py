"""10장 서버 쪽 연습문제 (10-4 세션 만료, 10-5 CORS).

    python3 server10ex.py

server10.py 의 로그인 방명록에 세션 만료와 CORS 허용 엔드포인트를 더했다.
쿠키에는 Max-Age·HttpOnly·SameSite 를 붙여 보낸다.
"""

import html
import random
import socket
import sys
import time
import urllib.parse

HOST, PORT = "", 8000
SESSION_MAX_AGE = 60 * 60          # 연습문제 10-4: 한 시간

# token -> {"data": {...}, "expires": timestamp}
SESSIONS = {}

ENTRIES = [("Pavel was here", "cerealkiller")]
LOGINS = {"crashoverride": "0cool", "cerealkiller": "emmanuel"}


def e(text):
    return html.escape(str(text), quote=True)


# ---------------------------------------------------------------------- #
# 연습문제 10-4: 만료되는 세션
# ---------------------------------------------------------------------- #

def expire_sessions(now=None):
    """지난 세션을 지운다. 이걸 안 하면 SESSIONS 가 끝없이 자란다."""
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
    """쓸 때마다 만료를 미룬다."""
    now = time.time() if now is None else now
    if token in SESSIONS:
        SESSIONS[token]["expires"] = now + SESSION_MAX_AGE


def new_token():
    return str(random.random())[2:]


# ---------------------------------------------------------------------- #
# 페이지
# ---------------------------------------------------------------------- #

def show_comments(session):
    out = "<!doctype html><html><head><title>방명록</title></head><body>"
    out += "<h1>방명록</h1>"
    for entry, who in ENTRIES:
        out += "<p>{} <i>by {}</i></p>".format(e(entry), e(who))
    if "user" in session:
        nonce = new_token()
        session["nonce"] = nonce
        out += '<form action="/add" method="post">'
        out += '<p><input name="guest" value=""> '
        out += '<input name="nonce" type="hidden" value="{}">'.format(e(nonce))
        out += "<button>남기기</button></p></form>"
    else:
        out += '<p><a href="/login">로그인해서 글 남기기</a></p>'
    out += "</body></html>"
    return out


def login_form(session):
    return ("<!doctype html><html><head><title>로그인</title></head><body>"
            '<form action="/" method="post">'
            '<p>사용자: <input name="username" value=""></p>'
            '<p>암호: <input name="password" type="password" value=""></p>'
            "<p><button>로그인</button></p></form></body></html>")


def not_found(url, method):
    return ("<!doctype html><html><body><h1>{} {} 를 찾을 수 없습니다</h1>"
            "</body></html>").format(e(method), e(url))


def cors_page():
    return '{"ok": true}'


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
    username = params.get("username")
    password = params.get("password")
    if username in LOGINS and LOGINS[username] == password:
        session["user"] = username
        return True
    return False


def add_entry(session, params):
    if "user" not in session:
        return False
    if params.get("nonce") != session.get("nonce"):
        return False          # 본문의 CSRF 방어
    text = (params.get("guest") or "").strip()
    if not text:
        return False
    ENTRIES.append((text, session["user"]))
    return True


def do_request(session, method, url, headers, body):
    """(상태, 본문, 추가 헤더) 를 돌려준다."""
    extra = {}
    path = urllib.parse.unquote(url)

    # 연습문제 10-5: 이 주소만 교차 출처 요청을 허락한다
    if path == "/cors":
        origin = headers.get("origin")
        if origin:
            extra["Access-Control-Allow-Origin"] = origin
            extra["Access-Control-Allow-Credentials"] = "true"
        return "200 OK", cors_page(), extra
    if path == "/nocors":
        return "200 OK", cors_page(), extra

    if method == "POST":
        params = form_decode(body)
        if path == "/":
            do_login(session, params)
            return "200 OK", show_comments(session), extra
        if path == "/add":
            add_entry(session, params)
            return "200 OK", show_comments(session), extra
        return "404 Not Found", not_found(url, method), extra

    if path == "/":
        return "200 OK", show_comments(session), extra
    if path == "/login":
        return "200 OK", login_form(session), extra
    return "404 Not Found", not_found(url, method), extra


def handle_connection(conx):
    req = conx.makefile("b")
    method, url, version = req.readline().decode("utf8").split(" ", 2)

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
        # 연습문제 10-4: 만료를 함께 보낸다. HttpOnly 로 스크립트에서 숨긴다.
        response += ("Set-Cookie: token={}; SameSite=Lax; HttpOnly; "
                     "Max-Age={}\r\n").format(token, SESSION_MAX_AGE)
    for name, value in extra.items():
        response += "{}: {}\r\n".format(name, value)
    response += "Content-Length: {}\r\n".format(len(data))
    response += "Content-Type: text/html; charset=utf-8\r\n"
    response += "Referrer-Policy: no-referrer-when-downgrade\r\n"
    response += "Connection: close\r\n"
    response += "\r\n"
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
        conx, _ = s.accept()
        handle_connection(conx)


if __name__ == "__main__":
    main(sys.argv[1:])
