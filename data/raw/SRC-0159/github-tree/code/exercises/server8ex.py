"""8장 서버 쪽 연습문제 (8-6 게시판, 8-7 영속성).

    python3 server8ex.py            # http://localhost:8000/

server8.py 의 방명록을 주제별 게시판으로 넓히고, 글을 파일에 남겨서
서버를 다시 켜도 사라지지 않게 했다.

    8-6 게시판    주제마다 자기 URL 과 자기 글 목록. 홈에서 주제를 만든다
    8-7 영속성    글을 board.txt 에 한 줄씩 적어 두고 켤 때 다시 읽는다
"""

import html
import os
import socket
import sys
import urllib.parse

HOST, PORT = "", 8000
STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "board.txt")


# ---------------------------------------------------------------------- #
# 연습문제 8-7: 파일에 남기기
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


def normalize(topic):
    """URL 에 쓸 수 있는 주제 이름으로 다듬는다."""
    topic = (topic or "").strip().strip("/")
    if "/" in topic or "\t" in topic or "\n" in topic:
        return ""
    return topic


BOARD = Board()


# ---------------------------------------------------------------------- #
# 페이지
# ---------------------------------------------------------------------- #

def e(text):
    return html.escape(text, quote=True)


def home_page():
    """연습문제 8-6: 주제 목록과 새 주제 만들기."""
    items = "".join('<li><a href="/{0}">{1}</a></li>'.format(
        urllib.parse.quote(t), e(t)) for t in BOARD.names())
    return ("<!doctype html><html><head><title>게시판</title></head><body>"
            "<h1>게시판</h1>"
            "<ul>" + (items or "<li>아직 주제가 없습니다</li>") + "</ul>"
            '<form action="/" method="post">'
            '<p>새 주제: <input name="topic" value=""> '
            '<button>만들기</button></p>'
            "</form>"
            "</body></html>")


def topic_page(topic):
    items = "".join("<li>%s</li>" % e(x) for x in BOARD.entries(topic))
    path = "/" + urllib.parse.quote(normalize(topic))
    return ("<!doctype html><html><head><title>{0}</title></head><body>"
            "<h1>{0}</h1>"
            "<ul>{1}</ul>"
            '<form action="{2}" method="post">'
            '<p><input name="guest" value=""> '
            '<input name="sign" type="checkbox" value="yes"> 서명 '
            '<button>남기기</button></p>'
            "</form>"
            '<p><a href="/">주제 목록</a></p>'
            "</body></html>").format(
        e(normalize(topic)), items or "<li>아직 글이 없습니다</li>", path)


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
        params[urllib.parse.unquote_plus(name)] = urllib.parse.unquote_plus(value)
    return params


def do_request(method, url, headers, body):
    path = urllib.parse.unquote(url)
    if method == "POST":
        params = form_decode(body)
        if path == "/":
            BOARD.add_topic(params.get("topic", ""))
            return "200 OK", home_page()
        topic = normalize(path)
        if BOARD.has(topic) or topic:
            text = params.get("guest", "")
            if params.get("sign") == "yes":          # 8-4 체크박스가 여기 닿는다
                text += " (서명함)"
            BOARD.add_entry(topic, text)
            return "200 OK", topic_page(topic)
        return "404 Not Found", not_found(url, method)
    if method == "GET":
        if path == "/":
            return "200 OK", home_page()
        topic = normalize(path)
        if BOARD.has(topic):
            return "200 OK", topic_page(topic)
        return "404 Not Found", not_found(url, method)
    return "405 Method Not Allowed", not_found(url, method)


def handle_connection(conx):
    req = conx.makefile("b")
    line = req.readline().decode("utf8")
    method, url, version = line.split(" ", 2)
    assert method in ("GET", "POST")

    headers = {}
    while True:
        line = req.readline().decode("utf8")
        if line in ("\r\n", "\n", ""):
            break
        header, _, value = line.partition(":")
        headers[header.casefold()] = value.strip()

    body = None
    if "content-length" in headers:
        length = int(headers["content-length"])
        body = req.read(length).decode("utf8")

    status, page = do_request(method, url, headers, body)
    data = page.encode("utf8")
    response = "HTTP/1.0 {}\r\n".format(status)
    response += "Content-Length: {}\r\n".format(len(data))
    response += "Content-Type: text/html; charset=utf-8\r\n"
    # HTTP/1.0 이라 요청마다 끊는다. 안 적어 주면 브라우저가 소켓을 재사용한다.
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
