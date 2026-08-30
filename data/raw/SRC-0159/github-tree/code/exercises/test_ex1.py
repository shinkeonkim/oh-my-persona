"""1장 연습문제 검증.

네트워크 없이 돌도록, 응답을 마음대로 정할 수 있는 작은 HTTP 서버를 띄워 테스트한다.

    python3 test_ex1.py
"""

import gzip
import os
import socket
import tempfile
import threading
import unittest

import ex1


class FakeServer(threading.Thread):
    """요청 경로별로 미리 정해 둔 raw 응답을 그대로 돌려주는 서버."""

    daemon = True

    def __init__(self, routes):
        super().__init__()
        self.routes = routes
        self.requests = []
        self.connections = 0
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen()
        self.port = self.sock.getsockname()[1]

    def run(self):
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            self.connections += 1
            threading.Thread(target=self._serve, args=(conn,), daemon=True).start()

    def _serve(self, conn):
        f = conn.makefile("rb")
        while True:
            line = f.readline()
            if not line:
                break
            request = line.decode().strip()
            headers = {}
            while True:
                h = f.readline().decode()
                if h in ("\r\n", "\n", ""):
                    break
                k, _, v = h.partition(":")
                headers[k.casefold()] = v.strip()
            self.requests.append((request, headers))
            path = request.split(" ")[1] if " " in request else "/"
            conn.sendall(self.routes.get(path, self.routes.get("*", b"")))
        conn.close()

    def url(self, path="/"):
        return "http://127.0.0.1:{}{}".format(self.port, path)


def raw(status="200 OK", headers=(), body=b""):
    head = "HTTP/1.1 {}\r\n".format(status)
    for k, v in headers:
        head += "{}: {}\r\n".format(k, v)
    head += "\r\n"
    return head.encode() + body


def plain(body, extra=()):
    data = body.encode() if isinstance(body, str) else body
    return raw(headers=[("Content-Length", str(len(data)))] + list(extra), body=data)


class ExerciseTest(unittest.TestCase):
    def setUp(self):
        self._close_sockets()
        ex1.CACHE.clear()

    def tearDown(self):
        self._close_sockets()

    @staticmethod
    def _close_sockets():
        for s in ex1.SOCKETS.values():
            try:
                s.close()
            except OSError:
                pass
        ex1.SOCKETS.clear()

    # 1-1 --------------------------------------------------------------
    def test_1_1_request_headers(self):
        srv = FakeServer({"*": plain("ok")}); srv.start()
        ex1.URL(srv.url()).request()
        request, headers = srv.requests[0]
        self.assertTrue(request.startswith("GET / HTTP/1.1"))
        self.assertIn("host", headers)
        self.assertIn("user-agent", headers)
        self.assertIn("connection", headers)

    # 1-2 --------------------------------------------------------------
    def test_1_2_file_scheme(self):
        fd, path = tempfile.mkstemp(suffix=".html", text=True)
        with os.fdopen(fd, "w") as f:
            f.write("<b>local</b>")
        try:
            self.assertEqual(ex1.URL("file://" + path).request(), "<b>local</b>")
        finally:
            os.unlink(path)

    # 1-3 --------------------------------------------------------------
    def test_1_3_data_scheme(self):
        url = ex1.URL("data:text/html,Hello world!")
        self.assertEqual(url.request(), "Hello world!")
        self.assertEqual(url.mediatype, "text/html")

    # 1-4 --------------------------------------------------------------
    def test_1_4_entities(self):
        self.assertEqual(ex1.lex("&lt;div&gt;"), "<div>")
        self.assertEqual(ex1.lex("<b>a &amp; b</b>"), "a & b")

    # 1-5 --------------------------------------------------------------
    def test_1_5_view_source(self):
        url = ex1.URL("view-source:data:text/html,<b>hi</b>")
        self.assertTrue(url.view_source)
        self.assertEqual(url.request(), "<b>hi</b>")
        self.assertEqual(ex1.lex(url.request()), "hi")

    # 1-6 --------------------------------------------------------------
    def test_1_6_keep_alive_reuses_socket(self):
        # 캐시(1-8)가 요청을 가로채면 소켓 재사용을 확인할 수 없으므로 no-store 로 막는다.
        srv = FakeServer({"*": plain("ok", [("Cache-Control", "no-store")])})
        srv.start()
        for _ in range(3):
            self.assertEqual(ex1.URL(srv.url()).request(), "ok")
        self.assertEqual(len(srv.requests), 3, "요청이 실제로 나가지 않았습니다")
        self.assertEqual(srv.connections, 1, "소켓이 재사용되지 않았습니다")

    def test_1_6_connection_close_drops_socket(self):
        srv = FakeServer({"*": plain("ok", [("Connection", "close")])}); srv.start()
        ex1.URL(srv.url()).request()
        self.assertEqual(ex1.SOCKETS, {})

    # 1-7 --------------------------------------------------------------
    def test_1_7_redirect_followed(self):
        srv = FakeServer({
            "/a": raw("301 Moved", [("Location", "/b"), ("Content-Length", "0")]),
            "/b": plain("도착"),
        })
        srv.start()
        self.assertEqual(ex1.URL(srv.url("/a")).request(), "도착")

    def test_1_7_redirect_loop_stops(self):
        srv = FakeServer({
            "*": raw("302 Found", [("Location", "/loop"), ("Content-Length", "0")]),
        })
        srv.start()
        with self.assertRaises(Exception):
            ex1.URL(srv.url("/loop")).request()

    # 1-8 --------------------------------------------------------------
    def test_1_8_cache_hit(self):
        srv = FakeServer({"*": plain("한번만")}); srv.start()
        url = srv.url()
        self.assertEqual(ex1.URL(url).request(), "한번만")
        self.assertEqual(ex1.URL(url).request(), "한번만")
        self.assertEqual(len(srv.requests), 1, "캐시가 쓰이지 않았습니다")

    def test_1_8_no_store(self):
        srv = FakeServer({"*": plain("매번", [("Cache-Control", "no-store")])})
        srv.start()
        url = srv.url()
        ex1.URL(url).request()
        ex1.URL(url).request()
        self.assertEqual(len(srv.requests), 2, "no-store 인데 캐시했습니다")

    def test_1_8_max_age(self):
        srv = FakeServer({"*": plain("잠깐", [("Cache-Control", "max-age=60")])})
        srv.start()
        ex1.URL(srv.url()).request()
        body, expires = ex1.CACHE[str(ex1.URL(srv.url()))]
        self.assertEqual(body, "잠깐")
        self.assertIsNotNone(expires)

    def test_1_8_unknown_directive_not_cached(self):
        srv = FakeServer({"*": plain("x", [("Cache-Control", "private")])})
        srv.start()
        ex1.URL(srv.url()).request()
        self.assertEqual(ex1.CACHE, {})

    # 1-9 --------------------------------------------------------------
    def test_1_9_gzip(self):
        packed = gzip.compress("압축된 본문".encode())
        srv = FakeServer({"*": raw(
            headers=[("Content-Encoding", "gzip"),
                     ("Content-Length", str(len(packed)))], body=packed)})
        srv.start()
        self.assertEqual(ex1.URL(srv.url()).request(), "압축된 본문")

    def test_1_9_chunked(self):
        body = b"4\r\nWiki\r\n5\r\npedia\r\n0\r\n\r\n"
        srv = FakeServer({"*": raw(
            headers=[("Transfer-Encoding", "chunked")], body=body)})
        srv.start()
        self.assertEqual(ex1.URL(srv.url()).request(), "Wikipedia")

    def test_1_9_chunked_and_gzip(self):
        packed = gzip.compress(b"both")
        body = ("%x\r\n" % len(packed)).encode() + packed + b"\r\n0\r\n\r\n"
        srv = FakeServer({"*": raw(
            headers=[("Transfer-Encoding", "chunked"),
                     ("Content-Encoding", "gzip")], body=body)})
        srv.start()
        self.assertEqual(ex1.URL(srv.url()).request(), "both")


if __name__ == "__main__":
    unittest.main(verbosity=2)
